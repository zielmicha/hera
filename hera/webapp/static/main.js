$('.nav li').each(function() {
    var link = $(this).find('a')[0]
    if(link && link.getAttribute('href') == location.pathname) {
        $(this).addClass('active')
    }
})
