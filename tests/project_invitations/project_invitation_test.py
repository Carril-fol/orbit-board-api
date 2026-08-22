from project_invitations.models.project_invitation_model import InvitationStatus

URL_PREFIX = "/invitations/api/v1"

UNKNOWN_PROJECT_ID = 2_000_000_000


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


async def test_remove_invitation(authenticated_client, invitation_created, invitations_repo):
    response = await authenticated_client.delete(f"{URL_PREFIX}/{invitation_created.id}")
    assert response.status_code == 200
    assert await invitations_repo.get_invite_by_id(invitation_created.id) is None
