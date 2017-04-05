Understanding Scrapy
===

## Background
The purpose of this tutorial is to better understand the `Scrapy` infrastructure; how to use the tool; and applications that can be supported from the resource. This tutorial follows a specific use-case and is project oriented. Because of this, there will be areas within the tutorial that link to other tutorials and resources, because this is all one interconnected beast!

## Setup
Initially, I'm following [this tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html) from the official Scrapy site. The initial setup is easy enough, simply `cd` into the directory that you want to work in and run - 

```
scrapy startproject tutorial
```
Easy enough. 

## Initial file structure
The above command builds out the following file structure:

```
tutorial
|-- tutorial
	|-- spiders
		|--__init__.py
	|-- __init__.py
	|-- items.py
	|-- middlewares.py	
	|-- pipelines.py
	|-- settings.py
|-- scrapy.cfg
```
**File descriptors**
To understand the infrascture that's been built, let's break down the files and filepaths and what they are doing

*/tutorial*

| File        | Description  |
| ------------- |:---------:|
| */tutorial* | Project's Python module where code will be imported from |
| `scrapy.cfg` | Deployment configuration file |

*/tutorial/tutorial*

| File        | Description  |
| ------------- |:---------:|
| */spiders* | Directory for spiders to be placed |
| `__init__.py` | Marks package directory for project |
| `items.py` | Project items definition file |
| `middlewares.py` | Project middlewares to alter request/responses |
| `pipelines.py` | Project pipelines file |
| `settings.py` | Project settings file |

*/tutorial/spiders*

| File        | Description  |
| ------------- |:---------:|
| `__init__.py` | Marks package directory for spiders |

## What's the data I'm grabbing?
For this initial tutorial, we are scraping quotes from [this site](http://quotes.toscrape.com/). For future tutorials, I will build spiders for more...uh...*valuable* information.

## What am I doing with it?
Right now, not much. I'm just learning! 

## Workflow

**Step 1 - Create spider**

Create my "quotes" spider by creating [quotes_spider.py](tutorial/tutorial/spiders/quotes_spider.py). There are three main purposes for this script: 

As you can see, our Spider subclasses scrapy.Spider and defines some attributes and methods:

- Defining the spider's `name`. It must be unique within a project, that is, you can’t set the same name for different Spiders.
- Defining the function `start_requests()`, which gens an iterable of Requests which the Spider will begin to crawl from. Subsequent requests will be generated successively from these initial requests.
- Defining the function `parse()` to handle the response downloaded for each of the requests made. The `parse()` method usually parses the response, extracting the scraped data as dicts and also finding new URLs to follow and creating new requests (Request) from them.

**Step 2 - Running Spider**

`cd` into the main directory for the project - which is wherever the `scrapy.cfg` file exists. Once there, run -

```
scrapy crawl quotes
```
This will output two html files in the working directory - in this case, the two files only house the information on the URLs we've parsed. 

**Step 3 - Extracting Data**

First, to learn how to extract data use scrapy shell on the site to try selectors. We can use this tool by runnin - 

```
scrapy shell "http://quotes.toscrape.com/page/1/"
```
From this shell we can select CSS attributes or xpaths to extract our data from the URL in question. For instance, running

```
response.css('title::text').extract_first()
```
will extract the first element in the SelectorList (a list of elements that meet the criteria of our response). It's also possible to extract via SelectorList using regex. When we run 

```
response.css('title::text').re(r'Q\w+')
```
it will return the text item in the `<title>` element containing the regex definition `r'Q\w+'`

We can also use xpath expressions to scrape our data, which is awesome because those are super handy and easy to grab. Running

```
response.xpath('//title/text()').extract_first()
```
based on the xpath `//title/text()` expression returns an identical output to our `response.css` function. Xpath expressions are far more powerful than CSS selectors - as they include some of the text within the content of the element as well. 

Now that we know how to peek under the hood and extract values, we can productionalize the scraping by finding the right CSS selector or xpath expression that we want to grab for every URL.

We can mess around in the `scrapy shell` to see what are the proper tags or expressions we need to capture to pull the data we want -

```
scrapy shell "http://quotes.toscrape.com"
response.css("div.quote")
```
Running the above gives us the ability to see what other sub-elements exist for us to select on. We can also assign selectors to variables to then run new selectors off of -

```
quote = response.css("div.quote")[0]
```

Based on the quote object we've now defined, we can pull other elements (title, author, and tags) - 

```
title = quote.css("span.text::text").extract_first()
author = quote.css("small.author::text").extract_first()
tags = quote.css("div.tags a.tag::text").extract() # Extract the list of tags
```

Now that we know **what** to extract, we can iterate over all of the quotes elements and put them together into a Python dictionary - 

```
for quote in response.css("div.quote"):
	text = quote.css("span.text::text").extract_first()
	author = quote.css("small.author::text").extract_first()
	tags = quote.css("div.tags a.tag::text").extract()
	print(dict(text=text, author=author, tags=tags))
```

We can then embed this extraction logic back into our `quotes_spider.py` script - 

```Python
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
```

The spider now grabs the text, author, and tags associated with each of the <div.quote> class elements, but right now it simply prints out the results instead of storing them.

**Step 4 - Storing Results**

The simplest way to store results from a spider is to either write them to JSON or JSON Lines format. The benefit of using JSON Lines is that you can run the scraper more than once without it crashing - and each record is a separate line so not everything is stored to memory.

To store as JSON or JSON Lines and save to the directory, we run - 

```
scrapy crawl quotes -o quotes.json
scrapy crawl quotes -o quotes.jl
```

For the sake of industry standardization, stick with JSON format for crawling. Using JSON Lines may work for standalone side projects, but for anything open source JSON will likely be used.

**Step 5 - Making `scrapy` Even Better**

Now we know how to parse a single URL (or a list of URLs) - but what about following links within a URL to make it recursive (meaning: successive paging through)?

To do that, we first have to extract the link we want to follow. Looking at our quotes page, there is a link to the next page with the following HTML - 

```
<ul class="pager">
    <li class="next">
        <a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a>
    </li>
</ul>
```

Turning back to the `scrapy shell` we can try and extract this element - 

```
response.css('li.next a').extract_first()
```

But what we really want is the `href` attribute within the element - this is the source of the link URL. For that, Scrapy supports a CSS extension that let’s you select the attribute contents, like this - 

```
response.css('li.next a::attr(href)').extract_first()
```

We can then tweak our `quotes_spider.py` spider script to recursively move to the next page - 

```
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
```

The last chunk defining `next_page` to be yielded will loop through every page that contains the `link` class of the `<li>` element. The `parse()` function will look for the next page after extracting data and builds a new URL using the `urljoin()` function and yields a new request to the next page. Once that class-element no longer exists, the spider will stop crawling and the yielded results can be collected.

This is scrapy’s mechanism of following links: when you yield a request in a callback method, scrapy will schedule that request to be sent and register a callback method to be executed when that request finishes.

Using this, you can build complex crawlers that follow links according to rules you define, and extract different kinds of data depending on the page it’s visiting.

**Step 6 - Storing Results**

This will be the focus of the next tutorial, which will either be *Understaning Postgresql* or *Understanding dynamoDB* or some hodgepodge of both of those. 