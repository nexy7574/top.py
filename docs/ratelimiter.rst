.. py:currentmodule:: toppy

Internal Ratelimiter
====================

.. warning::
    While this is documented, you are not encouraged to modify how the library
    handles ratelimits. The defaults are curated to the active top.gg ratelimits,
    and modifying things (incorrectly) will break **every** function in toppy.

Ratelimiter class
-----------------

.. autoclass:: toppy.ratelimiter.bucket.Ratelimit
    :members: