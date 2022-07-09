#!/usr/bin/env python
import os
import sys
import logging
import rich.console
from Bio import SeqIO
import glob
import s_rna_tools.utils
from s_rna_tools.rna_blast import RnaBlast
from halo import Halo

log = logging.getLogger(__name__)
stderr = rich.console.Console(
    stderr=True,
    style="dim",
    highlight=False,
    force_terminal=s_rna_tools.utils.rich_force_colors(),
)


class FindMatch:
    def __init__(self, in_file=None, m_file=None, out_folder=None, known_match="known"):
        if in_file is None:
            in_file = s_rna_tools.utils.prompt_path(
                msg="Select the fasta file with the sequences"
            )
        self.in_file = in_file
        if not os.path.isfile(self.in_file):
            log.error("fasta file %s does not exist ", self.in_file)
            stderr.print(f"[red] fasta data file {self.in_file} does not exist")
            sys.exit(1)
        if m_file is None:
            m_file = s_rna_tools.utils.prompt_path(
                msg="Select the file to match against the sequences"
            )
        self.m_file = m_file
        if not os.path.isfile(self.m_file):
            log.error("matching file %s does not exist ", self.m_file)
            stderr.print(f"[red] matching file {self.m_file} does not exist")
            sys.exit(1)
        if out_folder is None:
            out_folder = s_rna_tools.utils.prompt_path(
                msg="Select the folder to save results"
            )
        self.out_folder = out_folder
        self.known_match = known_match

    def create_blast_instance(self):
        return RnaBlast(self.in_file, "blastn-short", 90, 0.05, self.out_folder)

    def extract_sequences(self):
        sequences = {}
        for seq_record in SeqIO.parse(self.m_file, "fasta"):
            sequences[str(seq_record.seq)] = str(seq_record.id)
        return sequences

    def get_match_sequences(self):
        spinner = Halo(text='Creating Blast index', spinner='dots')
        spinner.start()
        blast_obj = self.create_blast_instance()
        spinner.succeed('Created index')
        spinner.start("Executing blast")
        if self.known_match == "unknown":
            unknow_seq = {}
            m_sequences = self.extract_sequences()
            tmp_folder = os.path.join(self.out_folder,"tmp_seq")
            os.makedirs(tmp_folder, exist_ok=True)
            # Create new temporary file for each of sequences
            for m_sequence, seq_id in m_sequences.items():
                q_file = os.path.join(tmp_folder,seq_id + ".fa")
                with open (q_file, "w") as fh:
                    fh.write("> " + seq_id + "\n")
                    fh.write(m_sequence)
                blast_res = blast_obj.run_blast(q_file)
                # delete temp file
                os.remove(q_file)
                if "not_match" in blast_res:
                    unknow_seq[seq_id] = m_sequence
            import pdb; pdb.set_trace()

        else:
            blast_res = blast_obj.run_blast(self.m_file)
            if "match" in blast_res:
                out_file = os.path.join(self.out_folder, "blast_results.tsv")
                blast_obj.write_to_file(blast_res, out_file)
            else:
                stderr.print("Not found any match with the query file")
        spinner.succeed()
        spinner.stop()
        import pdb; pdb.set_trace()
