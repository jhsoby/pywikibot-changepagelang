# pywikibot-changepagelang

This script sets page languages for a selection of pages decided by default Pywikibot page generators.

## Use
There are two things you need to do to use this script:

1. Copy the file `change_pagelang.py` into Pywikibot's core/scripts directory.
2. Copy the file `setlangpatch.patch` into Pywikibot's core directory and run `git apply setlangpatch.patch`, **or**:

Change the file `api.py` in pywikibot's pywikibot/data directory the following way:

There's a list of values under `self.write = self.action in` (line 1420 as of 4 December 2018); in this list, add `'setpagelanguage'`.

When this is done, you can use the script like other scripts in Pywikibot:

`python pwb.py change_pagelang [generator] -setlang:[language code]`

## Parameters
There is one obligatory parameter, `-setlang`, which is the language pages should be set to.

There are two mutually exclusive optional parameters, `-always` and `-never`. These come into play if a page already has a language set that is different from the wiki's content language; if you use -always, the bot will always change the language to what you have in setlang. If you use -never, the bot will never change the language if it has already been set.

If you use neither, you will be prompted about what to do in each case where the language is already set. You will not be prompted if the page doesn't have a specific language set – then the bot will just make the change.

## Example use
To set all pages with the prefix "Page:Salmai girje.pdf" to language `se`, use:

`python pwb.py change_pagelang -prefixindex:"Page:Salmai girje.pdf" -setlang:se`

To set all pages in [[Category:Hindi]] to language `hi`, regardless of whether they have another language set, use:

`python pwb.py change_pagelang -cat:Hindi -setlang:hi -always`
