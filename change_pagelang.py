#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script changes the content language of pages.


These command line parameters can be used to specify which pages to work on:

&params;

Furthermore, the following command line parameters are supported:

-setlang          What language the pages should be set to

-always           If a language is already set for a page, always change it
                  to the one set in -setlang.

-never            If a language is already set for a page, never change it to
                  the one set in -setlang (keep the current language).


"""
#
# (C) Jon Harald Søby, 2018
# (C) Pywikibot team, 2018
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals

import pywikibot
from pywikibot import i18n, pagegenerators, Bot
import pywikibot.data.api as api
from pywikibot.tools.formatter import color_format

docuReplacements = {
    '&params;': pagegenerators.parameterHelp,
}

class ChangeLangBot(Bot):

    """Change page language bot."""

    def __init__(self, generator, **kwargs):
        """Initializer."""
        self.availableOptions.update({
            'always': True,
            'never': True
        })
        self.setlang = kwargs.pop('setlang', None)
        super(ChangeLangBot, self).__init__(**kwargs)

        self.generator = generator

    def treat(self, page):
        """Treat a page."""
        def changelang(page):
            token = api.Request(parameters={'action': 'query', 'meta': 'tokens'},
                        site=pywikibot.Site()).submit()["query"]["tokens"]["csrftoken"]
            api.Request(parameters={'action': 'setpagelanguage', 'title': page.title(),
                        'lang': self.setlang, 'token': token
                        }, site=pywikibot.Site()).submit()
            pywikibot.output(color_format('{lightpurple}{0}{default}: Setting '
                        'page language to {green}{1}{default}',
                        page.title(as_link=True), self.setlang))

        # Current content language of the page and site language
        langcheck = api.Request(parameters={'action': 'query', 'prop': 'info',
                                  'titles': page.title(), 'meta': 'siteinfo'},
                                  site=pywikibot.Site()).submit()["query"]
        currentlang = ""
        for k in langcheck["pages"]:
            currentlang = langcheck["pages"][k]["pagelanguage"]
        sitelang = langcheck["general"]["lang"]
        if self.setlang == currentlang:
            pywikibot.output(color_format('{lightpurple}{0}{default}: This page '
                            'is already set to {green}{1}{default}; skipping.',
                            page.title(as_link=True), self.setlang))
        elif currentlang != sitelang:
            if self.options["always"]:
                changelang(page)
            elif self.options["never"]:
                pywikibot.output(color_format('{lightpurple}{0}{default}: This page '
                            'already has a different content language '
                            '{yellow}{1}{default} set; skipping.',
                            page.title(as_link=True), currentlang))
            else:
                pywikibot.output(color_format(
                    '\n\n>>> {lightpurple}{0}{default} <<<', page.title()))
                choice = pywikibot.input_choice(color_format('The content language '
                            'for this page is already set to '
                            '{yellow}{0}{default}, which is different from the '
                            'default ({1}). Change it to {green}{2}{default} '
                            'anyway?', currentlang, sitelang, self.setlang),
                            [('Always', 'a'), ('Yes', 'y'), ('No', 'n'),
                            ('Never', 'v')], default='Y')
                if choice == 'y':
                    changelang(page)
                if choice == 'n':
                    pywikibot.output('Skipping ...\n')
                if choice == 'a':
                    self.options['always'] = True
                    changelang(page)
                if choice == 'v':
                    self.options['never'] = True
                    pywikibot.output('Skipping ...\n')
        else:
            changelang(page)


    def run(self):
        """Run the bot."""
        for page in self.generator:
            self.treat(page)



def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: unicode
    """
    options = {
        "always": False,
        "never": False,
        "setlang": False
    }

    # Process global args and prepare generator args parser
    local_args = pywikibot.handle_args(args)
    genFactory = pagegenerators.GeneratorFactory()

    site = pywikibot.Site()

    for arg in local_args:
        if arg.startswith('-setlang:'):
            options[arg[1:len('-setlang')]] = arg[len('-setlang:'):]
        elif arg in ['-always', '-a']:
            options["always"] = True
        elif arg in ['-never', '-n']:
            options["never"] = True
        else:
            genFactory.handleArg(arg)

    if not options["setlang"]:
        pywikibot.error("No -setlang parameter given.")
        return False

    specialpages = api.Request(parameters={'action': 'query', 'meta': 'siteinfo', 'siprop': 'specialpagealiases'},
                    site=site).submit()["query"]["specialpagealiases"]
    specialpagelist = [specialpages[x]["realname"] for x in range(len(specialpages))]
    allowedlanguages = api.Request(parameters={'action': 'paraminfo', 'modules': 'setpagelanguage'},
                    site=site).submit()["paraminfo"]["modules"][0]["parameters"][2]["type"]
    # Check if the special page PageLanguage is enabled on the wiki
    # If it is not, page languages can't be set, and there's no point in
    # running the bot any further
    if not "PageLanguage" in specialpagelist:
        pywikibot.error("This site doesn't allow changing the "
                        "content languages of pages; aborting.")
        return False
    # Check if the account has the right to change page content language
    # If it doesn't, there's no point in running the bot any further.
    elif not "pagelang" in site.userinfo["rights"]: # TODO: Add "not"
        pywikibot.error("Your account doesn't have sufficient "
                        "rights to change the content language of pages; "
                        "aborting.\n\nYou must have the 'pagelang' right "
                        "in order to make this change.")
        return False
    # Check if the language you are trying to set is allowed.
    elif options["setlang"] not in allowedlanguages:
        pywikibot.error("'{}' is not in the list of allowed language codes; aborting.\n\n"
                        "The following is the list of allowed languages. Using "
                        "'default' will unset any set language and use the default "
                        "language for the wiki instead.\n\n"
                        .format(options["setlang"]) + ", ".join(allowedlanguages))
        return False
    else:
        gen = genFactory.getCombinedGenerator(preload=True)
        if gen:
            bot = ChangeLangBot(gen, **options)
            bot.run()
            return True
        else:
            pywikibot.bot.suggest_help(missing_generator=True)
            return False


if __name__ == '__main__':
    main()
