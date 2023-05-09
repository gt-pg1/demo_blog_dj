function limitCharacters(editor) {
    editor.on('submit', function(e) {
        var numChars = tinymce.activeEditor.plugins.wordcount.body.getCharacterCount();
        if (numChars > 2000) {
            alert("Maximum 2000 characters allowed.");
            e.preventDefault();
            return false;
        }
    });
}
