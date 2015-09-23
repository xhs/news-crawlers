
function getEntries() {
    var results = document.querySelectorAll('div.searchResults ol>li')
    var entries = []

    for (var i = 0; i < results.length; i++) {
        var result = results[i]
        var link = result.querySelector('div.element2 h3>a')
        var articleUrl = link.href
        var articleTitle = link.text

        var summary = result.querySelector('p.summary')
        var articleSummary = summary.textContent

        var timestamp = result.querySelector('div.storyMeta span.dateline')
        var articleTimestamp = timestamp.textContent

        entries.push({
            'url': articleUrl,
            'title': articleTitle,
            'summary': articleSummary,
            'timestamp': articleTimestamp
        })
    }

    return entries
}

function generateUrl(pageNumber) {
    return 'http://query.nytimes.com/search/sitesearch/?action=click&region=Masthead&pgtype=SectionFront&module=SearchSubmit&contentCollection=world&t=qry323#/*/since1851/allresults/' + pageNumber + '/allauthors/relevance/World/'
    //return 'http://query.nytimes.com/search/sitesearch/?action=click&region=Masthead&pgtype=SectionFront&module=SearchSubmit&contentCollection=world&t=qry323#/*/365days/allresults/' + pageNumber + '/allauthors/relevance/World/'
}

var server = require('webserver').create()
var system = require('system')
var port = system.env.PORT || 9999

var service = server.listen(port, function (request, response) {
    var page = new WebPage()

    var splittedPath = request.url.split('/')
    var pageNumber = splittedPath.pop()
    var url = generateUrl(pageNumber)
    console.log('retrieving url: ' + url)

    page.open(url, function () {
        console.log('page retrieved')

        var entries = page.evaluate(getEntries)

        response.statusCode = 200
        response.write(JSON.stringify({
            'entries': entries
        }))
        response.close()

        page.close()
    })
})

if (service) {
    console.log('server started - http://localhost:' + port)
}
