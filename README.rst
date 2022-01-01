.. image:: https://img.shields.io/pypi/v/mailie.svg
        :target: https://pypi.python.org/pypi/mailie

.. image:: https://img.shields.io/badge/Documentation-Docs-brightgreen
        :target: https://symonk.github.io/mailie/
        :alt: Documentation

.. image:: https://codecov.io/gh/symonk/mailie/branch/main/graph/badge.svg?token=C0R5875AU7
    :target: https://codecov.io/gh/symonk/mailie


Mailie
=======

Mailie is a multi purpose email library for python, comprised of the following:


 - A simple email DSL.
 - A powerful command line tool.
 - Load testing capabilities via async SMTP conversations.
 - Extensibility and hook/plugin system.


Two things to keep in mind for mailie is that:

 - Mailie currently relies on both `aiofiles` (for attachment parsing in cases of both normal and inline attachments).
 - Results of sending mail relies heavily on the MUA that the recipient is using, mailie does not attempt to circumvent any oddities here and you should be aware that mileage may vary for identicle emails.

Mailie supports async smtp conversations as part of an initiative to speed up performance of email sending for genuine use, under no circumstances should you use this as a means to overload or cause a DOS style attack on infrastructure in which you do not fully own, period.

----

Features:
-----------------

 - Synchronous and Asynchronous SMTP clients.
 - Simple plaintext emails.
 - Simple multipart/alternative emails (text/HTML etc).
 - Complex multipart/mixed emails.
 - Powerful attachment capabilities including entire directory support and mime type resolution.
 - A simple DSL for improved readability.
 - Load testing capabilities of an smtp server.
 - Powerful commandline tool that utilises the underlying DSL.
 - Support for plain, startTLS and TLS.

----

Using Mailie:
-----------------

Mailie can be installed via:

    .. code:: console


    pip install mailie

    mailie --help


-----

Contributing to Mailie:
-----------------

Todo ...

-----


Legalities:
------------
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
