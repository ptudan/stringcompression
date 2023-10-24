Basic Unicode size reduction algorithm

uses standard dictionary to replace common strings with numbers and space prefixes

naive algorithm just for changing the length of the raw unicode seems to work up to 25% byte reduction, see RESULTS.md

could possibly reserve rare punctuation marks instead of using the space-based approach, and instead create a special unicode version for that char

could be smarter at byte level

eg
two special bits at beginning of byte
00 - read next 6 bits for dictionary index
01 - read next 14 for dictionary index
11 - skip this byte and start to read as unicode until space

it may also be helpful to derive a way to include punctuation in the library, the point of the special_chars array

need to compare with LZ77 and DEFLATE https://blog.cloudflare.com/improving-compression-with-preset-deflate-dictionary/

however deflate seems to focus on single page content serving, whereas my algorithm here could theoretically be better for storing large amounts of text data
