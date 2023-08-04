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
from pathlib import Path
from dataclasses import dataclass
from .models import LicenseConfigHeader

__all__ = [
	"CommentSymbols",
	"OSSTemplate",
	"PrprTemplate",
	"HashSymbolExtMap",
	"StarSymbolExtMap",
	"HeaderData",
	"LicenseHeader"
]

Symbol = str | tuple[str, str]


class CommentSymbols:
	"""
	This class encapsulates the comment symbols for different programming languages.
	It holds the first, middle, and last symbols used to generate and insert license
	headers based on filetype. For each of the comment symbols, it can also contain an
	alias symbol used to identify pre-existing license headers in source code files.

	Properties:
		first: Property to return the first symbol or its alias.
		middle: Property to return the middle symbol or its alias.
		last: Property to return the last symbol or its alias.
		use_alias: Property to get or set the use_alias flag.
		has_alias: Property to return the status of has_alias flag.
		identical: Property to check if all symbols are identical.
	"""
	__has_alias__ = False
	__use_alias__ = False

	def __init__(self, *, first: Symbol, middle: Symbol, last: Symbol):
		"""
		Initializes the object with first, middle, and last comment symbols.
		All args must be either strings or tuples of strings.

		Args:
			first: The comment symbol of the first line of the license header block
			middle: The comment symbol of the next lines of the license header block
			last: The comment symbol of the last line of the license header block
		"""
		all_tuples = all([isinstance(x, tuple) for x in (first, middle, last)])
		all_strings = all([isinstance(x, str) for x in (first, middle, last)])

		if not all_tuples and not all_strings:
			raise TypeError("All arguments must be either strings or tuples.")

		self.__sym1__ = first if all_tuples else (first, first)
		self.__sym2__ = middle if all_tuples else (middle, middle)
		self.__sym3__ = last if all_tuples else (last, last)
		self.__has_alias__ = all_tuples

	@property
	def first(self) -> str:
		return self.__sym1__[1 if self.use_alias else 0]

	@property
	def middle(self) -> str:
		return self.__sym2__[1 if self.use_alias else 0]

	@property
	def last(self) -> str:
		return self.__sym3__[1 if self.use_alias else 0]

	@property
	def use_alias(self) -> bool:
		return self.__use_alias__

	@use_alias.setter
	def use_alias(self, value) -> None:
		self.__use_alias__ = value

	@property
	def has_alias(self) -> bool:
		return self.__has_alias__

	@property
	def identical(self) -> bool:
		return self.first == self.middle == self.last


class OSSTemplate:
	template = [
		"{title}",
		"",
		"Copyright (c) {year}, {holder}",
		"",
		"The contents of this file are subject to the terms and conditions defined in the License.",
		"You may not use, modify, or distribute this file except in compliance with the License.",
		"",
		"SPDX-License-Identifier: {spdx_id}"
	]


class PrprTemplate:
	template = [
		"Proprietary License",
		"",
		"Copyright (c) {year}, {holder}",
		"",
		"Unauthorized copying, modification, distribution, or publication of this software, ",
		"via any medium, is strictly prohibited without a written agreement from the copyright holder. ",
		"This software is proprietary and confidential."
		"",
		"All rights reserved."
	]


class HashSymbolExtMap:
	symbols = CommentSymbols(
		first='#',
		middle='#',
		last='#'
	)
	extensions = [
		".py", ".pyw", ".pyx", ".pxd", ".pxi", ".pyi",
		".rb", ".rbw",
		".pl", ".pm", ".t", ".pod",
		".sh", ".bash", ".ksh", ".csh", ".tcsh", ".zsh",
		".r", ".R", ".Rmd",
		".php", ".phtml", ".php4", ".php5", ".php7", ".phps",
		".lua",
		".tcl",
		".yaml", ".yml",
	]


class StarSymbolExtMap:
	symbols = CommentSymbols(
		first=('/*', '//'),
		middle=(' *', '//'),
		last=(' */', '//')
	)
	extensions = [
		".c", ".h",
		".cpp", ".hpp", ".cc", ".cxx", ".hxx",
		".cs",
		".java",
		".js", ".jsx",
		".css",
		".php", ".phtml", ".php4", ".php5", ".php7", ".phps",
		".swift",
		".go",
		".rs",
		".kt", ".kts",
		".ts", ".tsx",
		".sass", ".scss",
		".less",
		".scala",
		".groovy", ".gvy", ".gy", ".gsh"
	]


@dataclass(frozen=True)
class HeaderData:
	symbols: CommentSymbols
	extensions: list[str]
	text: str


class LicenseHeader:
	"""
	This class is responsible for the manipulation of file headers. It is
	primarily used to replace license headers in source code files. The class
	supports different types of comment symbols, and can handle shebang lines
	properly. It is initialized with a configuration object that defines the
	specifics of the license header.
	"""
	__headers__: list[HeaderData]

	def __init__(self, config: LicenseConfigHeader):
		"""
		Initializes the LicenseHeader object. It takes a LicenseConfigHeader object
		as parameter and constructs the header(s) to be used in the apply method.

		Args:
			config: Configuration object that specifies the header details.
		"""
		self.__headers__ = list()
		template = (OSSTemplate if config.oss else PrprTemplate).template
		indent = config.spaces * ' '

		for obj in [HashSymbolExtMap, StarSymbolExtMap]:
			header = [obj.symbols.first]

			for line in template:
				header.append(obj.symbols.middle + indent + line)
			header.append(obj.symbols.last + '\n')

			text = '\n'.join(header).format(
				title=config.title,
				year=config.year,
				holder=config.holder,
				spdx_id=config.spdx_id
			)
			data = HeaderData(
				symbols=obj.symbols,
				extensions=obj.extensions,
				text=text
			)
			self.__headers__.append(data)

	def apply(self, path: Path) -> None:
		"""
		Applies the previously constructed license header to the file at the specified path.
		If the file already has a license header, the code first checks if it should skip
		replacing the existing header if it's identical to the new header, otherwise the old
		license header will be replaced by the new one. The method is designed to properly
		handle shebang lines and supports various comment symbols depending on the file suffix.

		Args:
			path: A file path of type `pathlib.Path` to which the license header should be applied.

		Raises:
			FileNotFoundError: If the provided path is not a file.
			NotImplementedError: If the file type is not supported.
		"""
		if not path.is_file():
			raise FileNotFoundError(f"Cannot apply license header to non-file: {path}")

		header: HeaderData | None = None
		for obj in self.__headers__:
			if path.suffix in obj.extensions:
				header = obj
				break

		if not header:
			raise NotImplementedError(f"File type not supported: {path.suffix}")

		content = path.read_text().splitlines()

		shebang_line = ''
		if content and content[0].startswith('#!'):
			shebang_line = content.pop(0) + '\n'

		has_header = content[0].startswith(header.symbols.first)
		if not has_header and header.symbols.has_alias:
			header.symbols.use_alias = True

		if content[0].startswith(header.symbols.first):
			end = 0
			if header.symbols.identical:
				for i, line in enumerate(content):
					if line.startswith(header.symbols.first):
						end += 1
			else:
				for i, line in enumerate(content):
					if line.startswith(header.symbols.last):
						end += 1
						break
					elif (
						line.startswith(header.symbols.middle) or
						line.startswith(header.symbols.first) or
						len(line.strip()) == 0
					):
						end += 1
						continue

			old_header = '\n'.join(content[:end])
			if old_header == header.text.strip():
				return

			content = content[end:]

		content = '\n'.join(content).lstrip() + '\n'
		content = shebang_line + header.text + content

		path.write_text(content)
