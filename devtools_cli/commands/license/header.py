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
from abc import ABC
from pathlib import Path
from pydantic import BaseModel
from dataclasses import dataclass
from .models import LicenseConfigHeader

__all__ = [
	"CommentSymbols",
	"HeaderData",
	"HashSymbolHeaderData",
	"StarSymbolHeaderData",
	"HeaderTemplate",
	"LicenseHeader"
]


@dataclass(frozen=True)
class CommentSymbols:
	first: str
	middle: str
	last: str


class HeaderData(ABC, BaseModel):
	symbols: CommentSymbols
	extensions: list[str]
	text: str = ''


class HashSymbolHeaderData(HeaderData):
	symbols: CommentSymbols = CommentSymbols('#', '#', '#')
	extensions: list[str] = [
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


class StarSymbolHeaderData(HeaderData):
	symbols: CommentSymbols = CommentSymbols('/*', ' *', ' */')
	extensions: list[str] = [
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
	This class is responsible for the manipulation of file headers. It is
	primarily used to replace license headers in source code files. The class
	supports different types of comment symbols, and can handle shebang lines
	properly. It is initialized with a configuration object that defines the
	specifics of the license header.
	"""
	__headers__: [HeaderData]

	def __init__(self, config: LicenseConfigHeader):
		"""
		Initializes the LicenseHeader object. It takes a LicenseConfigHeader object
		as parameter and constructs the header(s) to be used in the apply method.

		Args:
			config: Configuration object that specifies the header details.
		"""
		self.__headers__ = list()
		template = HeaderTemplate()
		indent = config.spaces * ' '

		for obj in [StarSymbolHeaderData(), HashSymbolHeaderData()]:
			header = [obj.symbols.first]

			for line in template.text:
				header.append(obj.symbols.middle + indent + line)
			header.append(obj.symbols.last + '\n')

			obj.text = '\n'.join(header).format(
				title=config.title,
				year=config.year,
				holder=config.holder,
				spdx_id=config.spdx_id
			)
			self.__headers__.append(obj)

	def apply(self, path: Path) -> None:
		"""
		Applies the previously constructed license header to the file at the specified path.
		If the file already has a license header, the code first checks if it should skip
		replacing the existing header if it's identical to the new header, otherwise the old
		license header will be replaced by the new one. The method is designed to properly
		handle shebang lines and supports various comment symbols depending on the file suffix.

		Args:
			path: A file path of type `pathlib.Path` to which the license header should be applied.
		"""
		if not path.is_file():
			return

		header: HeaderData | None = None
		for obj in self.__headers__:
			if path.suffix in obj.extensions:
				header = obj

		if not header:
			return

		content = path.read_text().splitlines()

		shebang_line = ''
		if content and content[0].startswith('#!'):
			shebang_line = content.pop(0) + '\n'

		if content[0].startswith(header.symbols.first):
			end = 0
			if isinstance(header, HashSymbolHeaderData):
				for i, line in enumerate(content):
					if line.startswith(header.symbols.first):
						end += 1
			elif isinstance(header, StarSymbolHeaderData):
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
