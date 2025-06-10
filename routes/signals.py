from django.db.models.signals import post_save
from django.dispatch import receiver
from .sse.manager import SSEManager
from .models import Gameboard, Game


@receiver(post_save, sender=Gameboard)
def notify_new_board(sender, instance, created, **kwargs):
    if created:
        sse_manager = SSEManager()
        sse_manager.send_event(
            channel="notifications",
            event_type="newBoard",
            data={
                "board_id": instance.id,
                "board_name": instance.name,
                "creator_username": instance.user.username
            }
        )


@receiver(post_save, sender=Game)
def notify_new_game(sender, instance, created, **kwargs):
    if created:
        sse_manager = SSEManager()
        sse_manager.send_event(
            channel="notifications",
            event_type="newGame",
            data={
                "game_id": instance.id,
                "board_id": instance.gameboard.id,
                "board_name": instance.gameboard.name,
                "user_username": instance.user.username
            }
        )
