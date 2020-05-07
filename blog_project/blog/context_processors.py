from .models import Friend, FriendRequest


def friend_requests(request):
    user = request.user
    friend_request_count = FriendRequest.objects.filter(receiver_id=user.id).count()
    friend_count = Friend.objects.filter(current_user_id=user.id).count()
    return {
        "friend_request_count": friend_request_count,
        "friends_count": friend_count,
    }
