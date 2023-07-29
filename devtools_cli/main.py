#
#  MIT License
#
#  Copyright (c) 2023 Mattias Aabmets
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import inspect
import importlib
from typer import Typer
from pathlib import Path

app = Typer()

package_path = Path(__file__).parent
import_dir = package_path / "sub_apps"

for filepath in import_dir.rglob("*.py"):
	relative_path = filepath.relative_to(package_path)
	module_path = '.'.join(relative_path.with_suffix('').parts)
	module = importlib.import_module(
		package=package_path.name,
		name=f'.{module_path}'
	)

	for _, obj in inspect.getmembers(module):
		if isinstance(obj, Typer):
			app.registered_commands.extend([
				*obj.registered_commands
			])

	importlib.invalidate_caches()
