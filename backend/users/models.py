from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Follow(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='follower',
		verbose_name='Подписчик',
	)
	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='following',
		verbose_name='Автор',
	)
	subscription_date = models.DateField(
		auto_now_add=True, verbose_name='Дата подписки')

	class Meta:
		ordering = ['-id']
		verbose_name = 'Подписка'
		verbose_name_plural = 'Подписки'
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'author'], name='follow unique'
			)
		]
