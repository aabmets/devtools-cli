#
#   MIT License
#
#   Copyright (c) 2023, Mattias Aabmets
#
#   This file is subject to the terms and conditions defined in
#   the License. You may not use, modify, or distribute this file
#   except in compliance with the License.
#
#   SPDX-License-Identifier: MIT
#
from dataclasses import dataclass


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
		"{lic_name}",
		"",
		"Copyright (c) {cr_year}, {cr_holder}",
		"",
		"This file is subject to the terms and conditions defined in",
		"the License. You may not use, modify, or distribute this file",
		"except in compliance with the License.",
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
		lic_name (str): The license name, e.g., "MIT License".
		cr_year (str): The copyright year, e.g., "2023".
		cr_holder (str): The copyright holder, e.g., "John Doe".
		spdx_id (str): The SPDX license identifier, e.g., "MIT".
		spaces (int): The number of spaces to use for indentation in the license text.
		symbols (CommentSymbols): A CommentSymbols instance representing the comment
			symbols for the first, middle, and the last line of the license header block.
	"""

	def __init__(
			self,
			lic_name: str,
			cr_year: str,
			cr_holder: str,
			spdx_id: str,
			spaces: int,
			symbols: CommentSymbols
	):
		template = HeaderTemplate()
		header = [symbols.first]
		indent = spaces * ' '

		for line in template.text:
			header.append(symbols.middle + indent + line)
		header.append(symbols.last + '\n')

		self.text = '\n'.join(header).format(
			lic_name=lic_name,
			cr_year=cr_year,
			cr_holder=cr_holder,
			spdx_id=spdx_id
		)
