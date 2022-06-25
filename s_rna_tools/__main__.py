#!/usr/bin/env python
import logging
import emoji

# from rich.prompt import Confirm
import click
import rich.console
import rich.logging
import rich.traceback

import s_rna_tools.utils
import s_rna_tools.group_sequences

log = logging.getLogger()


def run_s_rna_tools():
    # Set up rich stderr console
    stderr = rich.console.Console(
        stderr=True, force_terminal=s_rna_tools.utils.rich_force_colors()
    )

    # Set up the rich traceback
    rich.traceback.install(console=stderr, width=200, word_wrap=True, extra_lines=1)
    stderr.print(
        "[yellow]    ____            ___                            ",
        highlight=False,
    )
    stderr.print(
        "[yellow]   /      [blue]__  __ [yellow]  |   \ |\   |    /\ ", highlight=False
    )
    stderr.print(
        "[yellow]   \___   [red]  \/   [yellow]  |__ / | \  |   /  \ ", highlight=False
    )
    stderr.print(
        "[yellow]       \  [blue]__/\__ [yellow]  |  \  |  \ |  /____\ ",
        highlight=False,
    )
    stderr.print(
        "[yellow]   ____/         [yellow]  |   \ |   \| /      \ ", highlight=False
    )

    __version__ = "0.0.1"
    stderr.print()
    stderr.print(
        "       ",
        emoji.emojize(":dna:"),
        "[bold grey39] s-rna-tools version {}".format(__version__),
        highlight=False,
    )
    stderr.print()

    # Lanch the click cli
    s_rna_tools_cli()


# Customise the order of subcommands for --help
class CustomHelpOrder(click.Group):
    def __init__(self, *args, **kwargs):
        self.help_priorities = {}
        super(CustomHelpOrder, self).__init__(*args, **kwargs)

    def get_help(self, ctx):
        self.list_commands = self.list_commands_for_help
        return super(CustomHelpOrder, self).get_help(ctx)

    def list_commands_for_help(self, ctx):
        """reorder the list of commands when listing the help"""
        commands = super(CustomHelpOrder, self).list_commands(ctx)
        return (
            c[1]
            for c in sorted(
                (self.help_priorities.get(command, 1000), command)
                for command in commands
            )
        )

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except capture
        a priority for listing command names in help.
        """
        help_priority = kwargs.pop("help_priority", 1000)
        help_priorities = self.help_priorities

        def decorator(f):
            cmd = super(CustomHelpOrder, self).command(*args, **kwargs)(f)
            help_priorities[cmd.name] = help_priority
            return cmd

        return decorator


@click.group(cls=CustomHelpOrder)
@click.version_option(s_rna_tools.__version__)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose output to the console.",
)
@click.option(
    "-l", "--log-file", help="Save a verbose log to a file.", metavar="<filename>"
)
def s_rna_tools_cli(verbose, log_file):

    # Set the base logger to output DEBUG
    log.setLevel(logging.DEBUG)

    # Set up logs to a file if we asked for one
    if log_file:
        log_fh = logging.FileHandler(log_file, encoding="utf-8")
        log_fh.setLevel(logging.DEBUG)
        log_fh.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(name)-20s [%(levelname)-7s]  %(message)s"
            )
        )
        log.addHandler(log_fh)


s_rna_tools_cli.command(help_priority=1)


@click.option("-f", "--file", help="fasta input file with sequences")
@click.option("-d", "--in_folder", help="password for the user to login")
@click.option("-o", "--out_folder", help="Path to save generated ouput files")
def group_sequences(file, in_folder, out_folder):
    """Group small RNA sequences."""
    new_s_group = group_sequences.GroupSequences(file, in_folder, out_folder)
    print(new_s_group)
