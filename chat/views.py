from pyexpat.errors import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from notifications.models import Notification
from .models import ChatRoom, ChatMessage
from rooms.models import *
from django.db.models import Max
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Exists, Max


@login_required
def initiate_chat(request, room_slug):
    room = get_object_or_404(Room, room_slug=room_slug)
    
    if request.user.user_type == 'customer':
        chat_room, created = ChatRoom.objects.get_or_create(
            room=room,
            customer=request.user,
            seller=room.seller
        )
    else:
        # Sellers can't initiate chats with other sellers
        return HttpResponseForbidden("Sellers can't initiate chats")
    
    return redirect('chat_room', room_id=chat_room.id)

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)

    # Verify user has access to this chat
    if request.user not in [chat_room.customer, chat_room.seller]:
        return HttpResponseForbidden("You don't have access to this chat")
    
    chat_room.mark_as_read(request.user)

    messages = ChatMessage.objects.filter(chat_room=chat_room).order_by('timestamp')
    
    # # Mark messages as read when opening chat
    # if request.user == chat_room.customer or request.user == chat_room.seller:
    #     chat_room.mark_as_read(request.user)
    
    # Get all chat rooms for the sidebar
    if request.user.user_type == 'customer':
        chat_rooms = ChatRoom.objects.filter(customer=request.user)
    else:
        chat_rooms = ChatRoom.objects.filter(seller=request.user)
        
    
    return render(request, 'all_chats.html', {
        'current_chat': chat_room,
        'messages': messages,
        'chat_rooms': chat_rooms,
    })

@login_required
def customer_chat_list(request):
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    chat_rooms = ChatRoom.objects.filter(
        customer=request.user
    ).annotate(
        latest_message_time=Max('messages__timestamp'),
        has_real_unread=Exists(
            ChatMessage.objects.filter(
                chat_room=OuterRef('pk'),
                read=False,
                sender=OuterRef('seller')
            )
        )
    ).order_by('-latest_message_time', '-updated_at')

    # Update status based on actual messages
    for room in chat_rooms:
        room.has_unread_messages = room.has_real_unread
        room.save()

    return render(request, 'customer_chatlist.html', {
        'chat_rooms': chat_rooms,
        'current_chat': None,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,

    })


@login_required
def seller_chat_list(request):
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    chat_rooms = ChatRoom.objects.filter(
        seller=request.user
    ).annotate(
        latest_message_time=Max('messages__timestamp'),
        # Add this annotation to check for REAL unread messages from customers
        has_real_unread=Exists(
            ChatMessage.objects.filter(
                chat_room=OuterRef('pk'),
                read=False,
                sender=OuterRef('customer')  # Customer's unread messages to seller
            )
        )
    ).order_by('-latest_message_time', '-updated_at')

    # Sync the flag with actual unread status
    for room in chat_rooms:
        if room.has_unread_messages != room.has_real_unread:
            room.has_unread_messages = room.has_real_unread
            room.save()
        # Still call update_unread_status for WebSocket consistency
        room.update_unread_status()

    
    return render(request, 'seller_chatlist.html', {
        'chat_rooms': chat_rooms,
        'current_chat': None,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    })


# @login_required
# def delete_chat_room(request, room_id):
#     chat_room = get_object_or_404(ChatRoom, id=room_id)
#     if request.user not in [chat_room.customer, chat_room.seller]:
#         return HttpResponseForbidden("No permission")
#     chat_room.delete()
#     return redirect('customer_chat_list' if request.user.user_type == 'customer' else 'seller_chat_list')



