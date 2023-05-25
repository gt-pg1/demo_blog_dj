(function() {
    tinymce.PluginManager.add('blockquote_enter', function(editor, url) {
        editor.on('keydown', function(e) {
            if (e.keyCode === 13) {  // если нажат Enter
                var currentNode = editor.selection.getNode();
                var blockquoteNode = editor.dom.getParent(currentNode, 'blockquote');
                if (blockquoteNode) {
                    // Если текущий узел внутри blockquote, то...
                    e.preventDefault();  // отменить стандартное поведение
                    var p = editor.dom.create('p', {}, '\u00a0');  // создаем новый элемент <p> с неразрывным пробелом
                    editor.dom.insertAfter(p, blockquoteNode);  // вставляем его после текущего blockquote

                    var rng = editor.dom.createRng();  // создаем объект диапазона
                    rng.setStart(p, 0);  // устанавливаем начало диапазона в новый параграф
                    rng.setEnd(p, 0);  // устанавливаем конец диапазона в новый параграф
                    editor.selection.setRng(rng);  // перемещаем курсор в новый диапазон

                    // Добавляем прокрутку
                    editor.selection.scrollIntoView(p);
                }
            }
        });
    });
})();
