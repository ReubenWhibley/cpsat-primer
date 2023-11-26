Modelling
=========

CP-SAT provides us with much more modelling options than the classical
MIP-solver. Instead of just the classical linear constraints (<=, ==, >=), we
have various advanced constraints such as ``AllDifferent`` or
``AddMultiplicationEquality``. This spares you the burden of modelling the logic
only with linear constraints, but also makes the interface more extensive.
Additionally, you have to be aware that not all constraints are equally
efficient. The most efficient constraints are linear or boolean constraints.
Constraints such as ``AddMultiplicationEquality`` can be significantly(!!!) more
expensive.

   **If you are coming from the MIP-world, you should not overgeneralize your
   experience** to CP-SAT as the underlying techniques are different. It does not
   rely on the linear relaxation as much as MIP-solvers do. Thus, you can often
   use modelling techniques that are not efficient in MIP-solvers, but perform
   reasonably well in CP-SAT. For example, I had a model that required multiple
   absolute values and performed significantly better in CP-SAT than in Gurobi
   (despite a manual implementation with relatively tight big-M values).

This primer does not have the space to teach about building good models. In the
following, we will primarily look onto a selection of useful constraints. If you
want to learn how to build models, you could take a look into the book
`Model Building in Mathematical Programming by H. Paul Williams <https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330>`_
which covers much more than you probably need, including some actual
applications. This book is of course not for CP-SAT, but the general techniques
and ideas carry over. However, it can also suffice to simply look on some other
models and try some things out. If you are completely new to this area, you may
want to check out modelling for the MIP-solver Gurobi in this
`video course <https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9>`_.
Remember that many things are similar to CP-SAT, but not everything (as already
mentioned, CP-SAT is especially interesting for the cases where a MIP-solver
fails).

The following part does not cover all constraints. You can get a complete
overview by looking into the
`official documentation <https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel>`_.
Simply go to ``CpModel`` and check out the ``AddXXX`` and ``NewXXX`` methods.

Resources on mathematical modelling (not CP-SAT specific):

- `Math Programming Modeling Basics by Gurobi <https://www.gurobi.com/resources/math-programming-modeling-basics/>`_:
  Get the absolute basics.
- `Modeling with Gurobi Python <https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9>`_:
  A video course on modelling with Gurobi. The concepts carry over to CP-SAT.
- `Model Building in Mathematical Programming by H. Paul Williams <https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330>`_:
  A complete book on mathematical modelling.

Variables
~~~~~~~~~

There are two important types of variables in CP-SAT: Booleans and Integers
(which are actually converted to Booleans, but more on this later). There are
also, e.g.,
`interval variables <https://developers.google.com/optimization/reference/python/sat/python/cp_model#intervalvar>`_,
but they are not as important and can be modelled easily with integer variables.
For the integer variables, you have to specify a lower and an upper bound.

.. code-block:: python

   # integer variable z with bounds -100 <= z <= 100
   z = model.NewIntVar(-100, 100, "z")
   # boolean variable b
   b = model.NewBoolVar("b")
   # implicitly available negation of b:
   not_b = b.Not()  # will be 1 if b is 0 and 0 if b is 1

.. note::

  Having tight bounds on the integer variables can make a huge impact on the
  performance. It may be useful to run some optimization heuristics beforehand
  to get some bounds. Reducing it by a few percent can already pay off for some
  problems.

There are no continuous/floating point variables (or even constants) in CP-SAT:
If you need floating point numbers, you have to approximate them with integers
by some resolution. For example, you could simply multiply all values by 100 for
a step size of 0.01. A value of 2.35 would then be represented by 235. This
could probably be implemented in CP-SAT directly, but doing it explicitly is
not difficult, and it has numerical implications that you should be aware of.

The lack of continuous variables may sound like a serious limitation, especially
if you have a background in linear optimization (where continuous variables are
the "easy part"), but as long as they are not a huge part of your problem, you
can often work around it. I had problems with many continuous variables on which
I had to apply absolute values and conditional linear constraints, and CP-SAT
performed much better than Gurobi, which is known to be very good at continuous
variables. In this case, CP-SAT struggled less with the continuous variables
(Gurobi's strength), than Gurobi with the logical constraints (CP-SAT's
strength). In a further analysis, I noted an only logarithmic increase of the
runtime with the resolution. However, there are also problems for which a higher
resolution can drastically increase the runtime. The packing problem, which is
discussed further below, has the following runtime for different resolutions:
1x: 0.02s, 10x: 0.7s, 100x: 7.6s, 1000x: 75s, 10_000x: >15min. The solution was
always the same, just scaled, and there was no objective, i.e., only a feasible
solution had to be found. Note that this is just an example, not a
representative benchmark. See
`./examples/add_no_overlap_2d_scaling.ipynb <https://github.com/d-krupke/cpsat-primer/blob/rst/examples/add_no_overlap_2d_scaling.ipynb>`_
for the code. If you have a problem with a lot of continuous variables, such as
`network flow problems <https://en.wikipedia.org/wiki/Network_flow_problem>`_, you
are probably better served with a MIP-solver.

In my experience, boolean variables are by far the most important variables in
many combinatorial optimization problems. Many problems, such as the famous
Traveling Salesman Problem, only consist of boolean variables. Implementing a
solver specialized on boolean variables by using a SAT-solver as a base, such as
CP-SAT, thus, is quite sensible. The resolution of coefficients (in combination
with boolean variables) is less critical than for variables.