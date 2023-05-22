function paste_preprocess(plugin, args) {
    var content = args.content;

    // Remove all style attributes
    content = content.replace(/(<[^>]+) style=".*?"/gi, '$1');

    // Remove all class attributes
    content = content.replace(/(<[^>]+) class=".*?"/gi, '$1');

    // Remove all tags except p, ol, ul, li, strong, em, h1, h2, h3
    content = content.replace(/<(?!\/?(p|ol|ul|li|strong|b|em|h[123]))[^>]+>/gi, '');

    // Return the cleaned content
    args.content = content;
}