console.log('custom.js loaded!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, processing links...');
    var links = document.links;
    console.log('Found', links.length, 'links');
    
    for (var i = 0; i < links.length; i++) {
        var link = links[i];
        if (link.hostname !== window.location.hostname && link.hostname !== '') {
            console.log('Setting target=_blank for:', link.href);
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        }
    }
});