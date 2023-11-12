.. cpsat-primer documentation master file, created by
   sphinx-quickstart on Tue Nov  7 19:56:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Using and Understanding ortools' CP-SAT: A Primer and Cheat Sheet
=================================================================

*By Dominik Krupke, TU Braunschweig*

**This tutorial is under** `CC-BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_ **.Smaller parts can be copied without
any acknowledgement for non-commercial, educational purposes. Contributions are very welcome, even if it is just spell-checking.**

.. warning::

   **You are reading a draft! Expect lots of mistakes (and please report them either as an issue or pull request :) )**


Many `combinatorially difficult <https://en.wikipedia.org/wiki/NP-hardness>`_  optimization problems can, despite their proven theoretical hardness, be solved reasonably well in practice.
The most successful approach is to use `Mixed Integer Linear Programming <https://en.wikipedia.org/wiki/Integer_programming>`_ (MIP) to model the problem and then use a solver to find a solution.
The most successful solvers for MIPs are `Gurobi <https://www.gurobi.com/>`_ and `CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`_, which are both commercial and expensive (though, free for academics).
There are also some open source solvers, but they are often not as powerful as the commercial ones.
However, even when investing in such a solver, the underlying techniques (`Branch and Bound <https://en.wikipedia.org/wiki/Branch_and_bound>`_
& `Cut <https://en.wikipedia.org/wiki/Branch_and_cut>`_ on `Linear Relaxations <https://en.wikipedia.org/wiki/Linear_programming_relaxation>`_) struggle with some optimization problems, especially if the problem contains a lot of logical constraints that a solution has to satisfy.
In this case, the `Constraint Programming <https://en.wikipedia.org/wiki/Constraint_programming>`_ (CP) approach may be more successful.
For Constraint Programming, there are many open source solvers, but they are often not as powerful as the commercial MIP-solvers.
While MIP-solvers are frequently able to solve problems with hundreds of thousands of variables and constraints, the classical CP-solvers often struggle with problems with more than a few thousand variables and constraints.
However, the relatively new `CP-SAT <https://developers.google.com/optimization/cp/cp_solver>`_ of Google's `ortools <https://github.com/google/or-tools/>`_
suite shows to overcome many of the weaknesses and provides a viable alternative to MIP-solvers, being competitive for many problems and sometimes even superior.

This unofficial primer shall help you use and understand this powerful tool, especially if you are coming from
the `Mixed Integer Linear Programming <https://en.wikipedia.org/wiki/Integer_programming>`_ -community, as
it may prove useful in cases where Branch and Bound performs poorly.

If you are relatively new to combinatorial optimization, I suggest you to read the relatively short book `In Pursuit of the Traveling Salesman by Bill Cook <https://press.princeton.edu/books/paperback/9780691163529/in-pursuit-of-the-traveling-salesman>`_ first.
It tells you a lot about the history and techniques to deal with combinatorial optimization problems, on the example of the famous `Traveling Salesman Problem <https://en.wikipedia.org/wiki/Travelling_salesman_problem>`_.
The Traveling Salesman Problem seems to be intractable already for small instances, but it is actually possible to solve instances with thousands of cities in practice.
It is a very light read and you can skip the more technical parts if you want to.
As an alternative, you can also read this `free chapter, coauthored by the same author <https://www.math.uwaterloo.ca/~bico/papers/comp_chapter1.pdf>`_ and 
watch this very amusing `YouTube Video (1hour) <https://www.youtube.com/watch?v=5VjphFYQKj8>`_.
If you are short on time, at least watch the video, it is really worth it.
While CP-SAT follows a slightly different approach than the one described in the book/chapter/video, it is still important to see why it is possible to do the seemingly impossible and solve such problems in practice, despite their theoretical hardness.
Additionally, you will have learned the concept of `Mathematical Programming <https://www.gurobi.com/resources/math-programming-modeling-basics/>`_, and know that the term "Programming" has nothing to do with programming in the sense of writing code (otherwise, additionally read the just given reference).

After that (or if you are already familiar with combinatorial optimization), the following content awaits you in this primer:

.. toctree::
   :hidden:
   :caption: content:

   installation
   example
   modelling
   parameters
   how-does-it-work
   large-neighborhood-search

**Content:**

1. :doc:`installation`: Quick installation guide.
2. :doc:`example`: A short example, showing the usage of CP-SAT.
3. :doc:`modelling`: An overview of variables, objectives, and constraints. The constraints make the most
   important part.
4. :doc:`parameters`: How to specify CP-SATs behavior, if needed. Timelimits, hints, assumptions,
   parallelization, ...
5. :doc:`how-does-it-work`: After we know what we can do with CP-SAT, we look into how CP-SAT will do all
   these things.
6. :doc:`large-neighborhood-search`: The use of CP-SAT to create more powerful heuristics.

**Target audience**:
   
   People (especially my students at TU Braunschweig) with some background
   in `integer programming <https://en.wikipedia.org/wiki/Integer_programming>`_
   / `linear optimization <https://en.wikipedia.org/wiki/Linear_programming>`_, who would like to know an actual viable
   alternative to `Branch and Cut <https://en.wikipedia.org/wiki/Branch_and_cut>`_. However, I try to make it
   understandable for anyone interested
   in `combinatorial optimization <https://en.wikipedia.org/wiki/Combinatorial_optimization>`_.

**About the (main) author**:

  `Dr. Dominik Krupke <https://krupke.cc>`_ is a postdoctoral researcher at the `Algorithms Group <https://www.ibr.cs.tu-bs.de/alg>`_ at TU Braunschweig,
  where he researches and teaches on how to solve NP-hard problems in practice. He started writing this primer as course material for his students,
  but continued and extended it (mostly in his spare time) to make it available to a wider audience.







