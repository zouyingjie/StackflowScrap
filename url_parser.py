# -*- coding: utf-8 -*-
import lxml
from bs4 import BeautifulSoup
from lxml import cssselect, html
import url_manager
from url_manager import cacheClient


# def lxml_scraper(html):
#     tree = lxml.html.fromstring(html)
#     results = {}
#     select = lxml.cssselect.CSSSelector('tr#places_%s__row> td.w2p_fw')
#     return results


# def lxml_parse_title(html):
#     re = "<h1 class=\"title\">"
#     tree = lxml.html.fromstring(html)
#     title_selector = lxml.cssselect.SelectorError('h1.title')
#     result = title_selector(tree)
#     return result


def bs_parse_title(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    title = ''
    h1 = soup.find('h1')
    if h1 is None:
        h2 = soup.find('h2', class_='title')
        if h2 is None:
            h3 = soup.find('h3', class_='title')
            if h3 is not None:
                title = h3.text
        else:
            title = h2.text
    else:
        title = h1.text
    if cacheClient.get_title_by_url(url) is None:
        cacheClient.set_title(title, url)


def bs_parse_stackoverflow_question(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    soup = BeautifulSoup(html, 'html.parser')
    question_div = soup.find("div", id=link_id)
    div_answer = question_div.find("div", class_='status answered')
    if div_answer is None:
        div_answer = question_div.find("div", class_='status answered-accepted')
    if div_answer is not None:
        print(div_answer.text)
        return link_id


def bs_has_answer(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    soup = BeautifulSoup(html, 'html.parser')
    question_div = soup.find("div", id=link_id)
    div_answer = question_div.find("div", class_='status answered')
    if div_answer is None:
        div_answer = question_div.find("div", class_='status answered-accepted')
    if div_answer is not None:
        return True
    else:
        return False


def bs_parse_stack_overflow_vote(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    soup = BeautifulSoup(html, "html.parser")
    question_div = soup.find("div", id=link_id)
    vote_strong = question_div.find("strong")
    return vote_strong.text


def lxml_parse_stackover_flow_question_title(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    tree = lxml.html.fromstring(html)
    css_div_question_link = lxml.cssselect.CSSSelector("div#%s > div.summary > h3 > a" % link_id)
    div_question = css_div_question_link(tree)
    if len(div_question) > 0:
        return div_question[0].text
    return None


def lxml_parse_stackoverflow_question_vote(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    tree = lxml.html.fromstring(html)
    css_div_question_link = lxml.cssselect.CSSSelector(
        "div#%s > div.statscontainer > div.stats > div.vote > div.votes > span.vote-count-post > strong " % link_id)
    div_question = css_div_question_link(tree)
    if len(div_question) > 0:
        return div_question[0].text
    return None


def lxml_parse_question_title_and_vote(link, html):
    link_id = 'question-summary-' + str(link).split("/")[2]
    html_tree = lxml.html.fromstring(html)
    question_div = html_tree.get_element_by_id(link_id)
    link = question_div.find_class('question-hyperlink')[0].text_content()
    votes = question_div.find_class("vote-count-post")[0].text_content()
    return [link, votes]
