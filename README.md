# regendoc

re-render examples in documentation

regendoc copies examples from documentation into custom folders and renders it


```rst

.. code:: python

   # content of example.py

   def test_fun():
      pass


.. code:: text

   $ pytest example.py
   ============================= test session starts ==============================
   platform linux -- Python 3.9.7, pytest-6.3.0.dev685+g581b021aa.d20210918, py-1.10.0, pluggy-1.0.0
   rootdir: /path/to/example
   plugins: hypothesis-6.14.8
   collected 1 item

   example.py .                                                             [100%]

   ============================== 1 passed in 0.01s ===============================
```
