function (editor) {{
        editor.on("submit", function (e) {{
            var numChars = tinymce.activeEditor.plugins.wordcount.body.getCharacterCount();
            if (numChars > 2500) {{
                alert("Maximum 2500 characters allowed.");
                e.preventDefault();
                return false;
            }}
        }});
    }}