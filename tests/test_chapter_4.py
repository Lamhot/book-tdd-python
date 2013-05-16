# -*- coding: utf-8 -*-
import unittest

from book_tester import (
    ChapterTest,
    CodeListing,
    Command,
    Output,
    parsed_html,
    parse_listing,
)

class Chapter4Test(ChapterTest):

    def test_listings_and_commands_and_output(self):
        chapter_4 = parsed_html.cssselect('div.sect1')[4]
        listings_nodes = chapter_4.cssselect('div.listingblock')
        self.listings = [p for n in listings_nodes for p in parse_listing(n)]

        # sanity checks
        self.assertEqual(type(self.listings[0]), Command)
        self.assertEqual(type(self.listings[1]), Output)
        self.assertEqual(type(self.listings[2]), CodeListing)

        self.start_with_checkout(4)

        self.run_command(Command('python manage.py runserver'))
        ft_run = self.run_command(self.listings[0])
        self.assert_console_output_correct(ft_run, self.listings[1])

        print '*' * 80
        #self.write_to_file(self.listings[2])
        #self.fail(self.run_command(self.listings[3]))
        #self.fail('last write_to_file is screwy')

        #print self.tempdir
        #import time
        #time.sleep(200)

        self.check_test_code_cycle(2)

        self.check_git_diff_and_commit(5)

        self.assertIn('wibble', self.listings[8])
        self.listings[8].was_checked = True
        self.assertIn('wibble', self.listings[9])
        self.listings[9].was_checked = True

        tests = self.run_command(self.listings[10])
        self.assert_console_output_correct(tests, self.listings[11])

        self.write_to_file(self.listings[12])
        self.check_test_code_cycle(13)
        self.check_test_code_cycle(16)
        self.write_to_file(self.listings[19])

        self.assert_all_listings_checked(self.listings)


if __name__ == '__main__':
    unittest.main()