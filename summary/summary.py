"""
Summary
-------

This plugin allows easy, variable length summaries directly embedded into the
body of your articles.
"""

from __future__ import unicode_literals
from pelican import signals
from pelican.generators import ArticlesGenerator, StaticGenerator, PagesGenerator
import re

def initialized(pelican):
    from pelican.settings import DEFAULT_CONFIG
    DEFAULT_CONFIG.setdefault('SUMMARY_BEGIN_MARKER',
                              '<!-- PELICAN_BEGIN_SUMMARY -->')
    DEFAULT_CONFIG.setdefault('SUMMARY_END_MARKER',
                              '<!-- PELICAN_END_SUMMARY -->')
    DEFAULT_CONFIG.setdefault('SUMMARY_USE_FIRST_PARAGRAPH', False)
    if pelican:
        pelican.settings.setdefault('SUMMARY_BEGIN_MARKER',
                                    '<!-- PELICAN_BEGIN_SUMMARY -->')
        pelican.settings.setdefault('SUMMARY_END_MARKER',
                                    '<!-- PELICAN_END_SUMMARY -->')
        pelican.settings.setdefault('SUMMARY_USE_FIRST_PARAGRAPH', False)

def extract_summary_s(instance, summary):
    begin_marker = instance.settings['SUMMARY_BEGIN_MARKER']
    end_marker   = instance.settings['SUMMARY_END_MARKER']
    use_first_paragraph = instance.settings['SUMMARY_USE_FIRST_PARAGRAPH']

    remove_markers = True
    begin_summary = -1
    end_summary = -1
    moreS = False

    content = instance._content

    if begin_marker:
        begin_summary = content.find(begin_marker)
    if end_marker:
        end_summary = content.find(end_marker)

    if begin_summary == -1 and end_summary == -1 and use_first_paragraph:
        begin_marker, end_marker = '<p>', '</p>'
        remove_markers = False
        begin_summary = content.find(begin_marker)
        end_summary = content.find(end_marker)
        begin_marker = instance.settings['SUMMARY_BEGIN_MARKER']

    if begin_summary == -1 and end_summary == -1:
        instance.has_summary = False
        return '', False


    # skip over the begin marker, if present
    if begin_summary == -1 or begin_summary > end_summary:
        begin_summary = 0
    else:
        begin_summary = begin_summary + len(begin_marker)

    if end_summary == -1:
        end_summary = None

    summary += content[begin_summary:end_summary]

    if remove_markers:
        # remove the markers from the content
        if begin_summary:
            content = content.replace(begin_marker, '', 1)
        if end_summary:
            content = content.replace(end_marker, '', 1)

    if begin_marker:
        begin_summary = content.find(begin_marker)
        if begin_summary != -1:
            moreS = True

    instance._content = content
    return summary, moreS


def extract_summary(instance):
    # if summary is already specified, use it
    # if there is no content, there's nothing to do
    if hasattr(instance, '_summary') and instance._summary != '':
        instance.has_summary = True
        return

    if not instance._content:
        instance.has_summary = False
        return

    moreS = True
    summary = ''
    while moreS:
        summary, moreS = extract_summary_s(instance, summary)

    if summary == '':
        return

    summary = re.sub(r"<div.*>", "", summary)
    summary = re.sub(r"</div>", "", summary)
    summary = summary.replace('\n', ' ').replace('\r', '')
    summary = re.sub(r"\s*[\.,:?\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]*\s*((?:</[a-z]{1,11}>)?\s*</[a-z]{1,11}>)\s*$", r"…\1", summary)

    instance._summary = summary
    instance.has_summary = True

def run_plugin(generator):
    for article in generator.articles:
        extract_summary(article)

def register():
    signals.initialized.connect(initialized)
    signals.article_generator_finalized.connect(run_plugin)
