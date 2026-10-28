from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
import base64
from .models import Voter, PoliticalParty, Vote, Party
from .forms import VoterForm


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    form = VoterForm
    list_display = ('name', 'aadhar_number', 'email', 'verified', 'has_face', 'has_fingerprint')
    change_form_template = 'admin/voting/voter/change_form.html'

    def has_face(self, obj):
        return bool(obj.face_image)
    has_face.boolean = True
    has_face.short_description = 'Face Registered'

    def has_fingerprint(self, obj):
        return bool(obj.fingerprint_data)
    has_fingerprint.boolean = True
    has_fingerprint.short_description = 'Fingerprint Registered'

    def save_model(self, request, obj, form, change):
        # Handle face image data
        face_image_data = request.POST.get('face_image_data')
        if face_image_data and face_image_data.startswith('data:image'):
            format, imgstr = face_image_data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)
            file_name = f"face_{obj.aadhar_number}.{ext}"
            obj.face_image.save(file_name, ContentFile(img_data), save=False)

        super().save_model(request, obj, form, change)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('generated_signature', 'timestamp', 'ballot_hash')
    actions = None 
    
    def has_add_permission(self, request):
        # Disable the "Add Vote" button in admin
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the "Change" button for votes in admin
        return False


# Register other models
admin.site.register(PoliticalParty)
admin.site.register(Party)