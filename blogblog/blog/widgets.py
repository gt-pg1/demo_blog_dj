from django_summernote.widgets import SummernoteWidget


class SecureSummernoteWidgetWithoutPicture(SummernoteWidget):
    def summernote_settings(self, *args, **kwargs):
        settings = super().summernote_settings(*args, **kwargs)
        settings['disableUpload'] = True
        settings['toolbar'] = [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['insert', ['link', 'table', 'hr']],
            ['view', ['fullscreen']],
        ]
        settings['disableDragAndDrop'] = True
        return settings
