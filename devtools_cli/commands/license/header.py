#
#   MIT License
#
#   Copyright (c) 2023, Mattias Aabmets
#
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#
#   SPDX-License-Identifier: MIT
#
from dataclasses import dataclass
from .models import HeaderConfig

__all__ = [
	"CommentSymbols",
	"HashSymbolExtMap",
	"StarSymbolExtMap",
	"HeaderTemplate",
	"LicenseHeader"
]


@dataclass(frozen=True)
class CommentSymbols:
	first: str
	middle: str
	last: str


@dataclass(frozen=True)
class HashSymbolExtMap:
	symbols = CommentSymbols('#', '#', '#')
	extensions = [
		"py", "pyw", "pyx", "pxd", "pxi", "pyi",
		"rb", "rbw",
		"pl", "pm", "t", "pod",
		"sh", "bash", "ksh", "csh", "tcsh", "zsh",
		"r", "R", "Rmd",
		"php", "phtml", "php4", "php5", "php7", "phps",
		"lua",
		"tcl",
		"yaml", "yml",
	]


@dataclass(frozen=True)
class StarSymbolExtMap:
	symbols = CommentSymbols('/*', ' *', ' */')
	extensions = [
		"c", "h",
		"cpp", "hpp", "cc", "cxx", "hxx",
		"cs",
		"java",
		"js", "jsx",
		"css",
		"php", "phtml", "php4", "php5", "php7", "phps",
		"swift",
		"go",
		"rs",
		"kt", "kts",
		"ts", "tsx",
		"sass", "scss",
		"less",
		"scala",
		"groovy", "gvy", "gy", "gsh"
	]


@dataclass(frozen=True)
class HeaderTemplate:
	text = [
		"{title}",
		"",
		"Copyright (c) {year}, {holder}",
		"",
		"The contents of this file are subject to the terms and conditions defined in the License.",
		"You may not use, modify, or distribute this file except in compliance with the License.",
		"",
		"SPDX-License-Identifier: {spdx_id}"
	]


class LicenseHeader:
	"""
	The LicenseHeader class represents a customizable license header.

	This header can be prepended to source code files. It provides the
	text of the header, with customizable license name, copyright year,
	copyright holder, and SPDX license identifier.

	It also accepts a number of spaces for indentation and a CommentSymbols
	instance for formatting the license block according to different comment styles.

	Attributes:
		text (str): A string representation of the license header text.

	Args:
		config (HeaderConfig): An instance of the HeaderConfig class, which contains
			the formatting values for the placeholders in the license header template.
		symbols (CommentSymbols): A CommentSymbols instance representing the comment
			symbols for the first, middle, and the last line of the license header block.
	"""

	def __init__(self, config: HeaderConfig, symbols: CommentSymbols):
		template = HeaderTemplate()
		indent = config.spaces * ' '
		header = [symbols.first]

		for line in template.text:
			header.append(symbols.middle + indent + line)
		header.append(symbols.last + '\n')

		self.text = '\n'.join(header).format(
			title=config.title,
			year=config.year,
			holder=config.holder,
			spdx_id=config.spdx_id
		)
