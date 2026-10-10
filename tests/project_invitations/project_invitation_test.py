from datetime import timedelta

from project_invitations.models.project_invitation_model import InvitationStatus
from shared.config.settings import settings

URL_PREFIX = "/invitations/api/v1"

UNKNOWN_PROJECT_ID = 2_000_000_000
UNKNOWN_USER_EMAIL = "nobody@example.com"


async def test_create_invitation(authenticated_client, invitation_data, invitations_repo, second_user):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 201

    token = response.json()["token"]
    assert response.json()["accept_url"] == f"{URL_PREFIX}/{token}/accept"
    assert response.json()["reject_url"] == f"{URL_PREFIX}/{token}/reject"

    invitation = await invitations_repo.get_by_token(token)
    assert invitation.id_invitee == second_user.id
    assert invitation.status == InvitationStatus.PENDING


async def test_get_received_invitations(second_client, invitation_created):
    response = await second_client.get(f"{URL_PREFIX}/received")
    assert response.status_code == 200

    invitations = response.json()["invitations"]
    assert invitations[0]["token"] == invitation_created.token
    assert invitations[0]["status"] == InvitationStatus.PENDING


async def test_get_received_invitations_of_another_user(authenticated_client):
    response = await authenticated_client.get(f"{URL_PREFIX}/received")
    assert response.status_code == 200
    assert response.json()["invitations"] == []


async def test_accept_invitation(second_client, invitation_created, invitations_repo, collaborators_repo):
    response = await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")
    assert response.status_code == 200

    invitation = await invitations_repo.get_by_token(invitation_created.token)
    assert invitation.status == InvitationStatus.ACCEPTED

    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        invitation_created.id_invitee,
        invitation_created.id_project,
    )
    assert collaborator is not None
    assert collaborator.role == invitation_created.role


async def test_reject_invitation(second_client, invitation_created, invitations_repo, collaborators_repo):
    response = await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/reject")
    assert response.status_code == 200

    invitation = await invitations_repo.get_by_token(invitation_created.token)
    assert invitation.status == InvitationStatus.REJECTED

    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        invitation_created.id_invitee,
        invitation_created.id_project,
    )
    assert collaborator is None


async def test_revoke_invitation(authenticated_client, second_client, invitation_created, invitations_repo):
    response = await authenticated_client.delete(f"{URL_PREFIX}/{invitation_created.id}")
    assert response.status_code == 200

    invitation = await invitations_repo.get_invite_by_id(invitation_created.id)
    assert invitation.status == InvitationStatus.REVOKED

    notifications = (await second_client.get("/notifications/api/v1/")).json()["notifications"]
    assert notifications[0]["type"] == "invitation_revoked"


async def test_revoke_answered_invitation(authenticated_client, second_client, invitation_created):
    await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")

    response = await authenticated_client.delete(f"{URL_PREFIX}/{invitation_created.id}")
    assert response.status_code == 400


async def test_revoke_invitation_as_non_owner(second_client, invitation_created):
    response = await second_client.delete(f"{URL_PREFIX}/{invitation_created.id}")
    assert response.status_code == 403


async def test_accept_revoked_invitation(authenticated_client, second_client, invitation_created):
    await authenticated_client.delete(f"{URL_PREFIX}/{invitation_created.id}")

    response = await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")
    assert response.status_code == 404


async def test_reinvite_after_rejection(authenticated_client, second_client, invitation_created, invitation_data):
    await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/reject")

    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 201

    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 409


async def test_reinvite_removed_collaborator(
    authenticated_client, second_client, invitation_created, invitation_data, collaborators_repo
):
    await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")
    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        invitation_created.id_invitee,
        invitation_created.id_project,
    )
    await authenticated_client.delete(f"/collaborators/api/v1/{collaborator.id}")

    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 201


async def test_invite_existing_collaborator(authenticated_client, second_client, invitation_created, invitation_data):
    await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")

    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 409


async def test_invite_yourself(authenticated_client, invitation_data):
    me = (await authenticated_client.get("/users/api/v1/me")).json()

    response = await authenticated_client.post(f"{URL_PREFIX}/", json={**invitation_data, "invitee_email": me["email"]})
    assert response.status_code == 409


async def test_invite_unknown_user(authenticated_client, invitation_data):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json={**invitation_data, "invitee_email": UNKNOWN_USER_EMAIL})
    assert response.status_code == 404


async def test_invite_without_email(authenticated_client, invitation_data):
    no_email = {k: v for k, v in invitation_data.items() if k != "invitee_email"}
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=no_email)
    assert response.status_code == 422


async def test_request_after_rejected_invitation(second_client, invitation_created):
    await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/reject")

    response = await second_client.post(
        f"/projects/api/v1/{invitation_created.id_project}/requests",
        json={"message": "Test message", "role": "MEMBER"},
    )
    assert response.status_code == 201


async def _expire(invitation, invitations_repo):
    invitation.created_at -= timedelta(seconds=settings.invitation_expires)
    await invitations_repo.update(invitation)


async def test_accept_expired_invitation(second_client, invitation_created, invitations_repo, collaborators_repo):
    await _expire(invitation_created, invitations_repo)

    response = await second_client.post(f"{URL_PREFIX}/{invitation_created.token}/accept")
    assert response.status_code == 410

    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        invitation_created.id_invitee,
        invitation_created.id_project,
    )
    assert collaborator is None


async def test_expired_invitation_not_received(second_client, invitation_created, invitations_repo):
    await _expire(invitation_created, invitations_repo)

    response = await second_client.get(f"{URL_PREFIX}/received")
    assert response.status_code == 200
    assert response.json()["invitations"] == []


async def test_reinvite_after_expiry(authenticated_client, invitation_data, invitation_created, invitations_repo):
    await _expire(invitation_created, invitations_repo)

    response = await authenticated_client.post(f"{URL_PREFIX}/", json=invitation_data)
    assert response.status_code == 201
