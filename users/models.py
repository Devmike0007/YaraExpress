from django.db import models
from django.contrib.auth.models import User
from PIL import Image, UnidentifiedImageError
import os


class UserProfile(models.Model):
    """Profil utilisateur avec photo"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='profile_pictures/default.svg')
    bio = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    def save(self, *args, **kwargs):
        """Redimensionne la photo lors de la sauvegarde"""
        super().save(*args, **kwargs)
        if self.photo:
            _, ext = os.path.splitext(self.photo.path)
            ext = ext.lower()
            # Ne pas tenter d'ouvrir les images vectorielles (SVG)
            if ext in ('.svg', '.svgz'):
                return
            try:
                with Image.open(self.photo.path) as img:
                    # Redimensionne si la taille est trop grande
                    if img.height > 300 or img.width > 300:
                        max_size = (300, 300)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        img.save(self.photo.path)
            except UnidentifiedImageError:
                # Pillow ne reconnaît pas le fichier -> ignorer le redimensionnement
                return
            except Exception:
                # En cas d'autres erreurs IO, éviter d'empêcher la sauvegarde
                return
