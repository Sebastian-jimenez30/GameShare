from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):
    enlace = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'title',
            'developer',
            'release_year',
            'purchase_price',
            'rental_price_per_hour',
            'rental_price_per_day',
            'available',
            'enlace'
        ]

    def get_enlace(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.get_absolute_url())
