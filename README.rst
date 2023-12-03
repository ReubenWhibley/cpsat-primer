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

**CONTENT:**

1. **Installation**: Quick installation guide.
2. **Example**: A short example, showing the usage of CP-SAT.
3. **Modelling**: An overview of variables, objectives, and constraints. The constraints make the most
   important part.
4. **Parameters**: How to specify CP-SATs behavior, if needed. Timelimits, hints, assumptions,
   parallelization, ...
5. **How-does-it-work**: After we know what we can do with CP-SAT, we look into how CP-SAT will do all
   these things.
6. **Benchmarking your Model**: How to benchmark your model and how to interpret the results.
7. **Large neighborhood search**: The use of CP-SAT to create more powerful heuristics.

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

Installation
------------

We are using Python 3 in this primer and assume that you have a working Python 3 installation as well as the basic knowledge to use it. There are also interfaces for other languages, 
but Python 3 is, in my opinion, the most convenient one, as the mathematical expressions in Python are very close to the mathematical notation (allowing you to spot mathematical errors much faster). 
Only for huge models, you may need to use a compiled language such as C++ due to performance issues. For smaller models, you will not notice any performance difference.

The installation of CP-SAT, which is part of the ortools package, is very easy and can be done via Python's package manager `pip <https://pip.pypa.io/en/stable/>`_.

.. code:: bash

   pip3 install -U ortools

This command will also update an existing installation of ortools.
As this tool is in active development, it is recommended to update it frequently.
We actually encountered wrong behavior, i.e., bugs, in earlier versions that then have
been fixed by updates (this was on some more advanced features, don't worry about
correctness with basic usage).

I personally like to use `Jupyter Notebooks <https://jupyter.org/>`_ for experimenting with CP-SAT.

What hardware do I need?
~~~~~~~~~~~~~~~~~~~~~~~~

It's important to note that for CP-SAT usage, you don't need the capabilities of
a supercomputer. A standard laptop is often sufficient for solving many
problems. The primary requirements are CPU power and memory bandwidth, with a
GPU being unnecessary.

In terms of CPU power, the key is balancing the number of cores with the
performance of each individual core. CP-SAT leverages all available cores,
implementing different strategies on each.
`Depending on the number of cores, CP-SAT will behave differently <https://github.com/google/or-tools/blob/main/ortools/sat/docs/troubleshooting.md#improving-performance-with-multiple-workers>`_.
However, the effectiveness of these strategies can vary, and it's usually not
apparent which one will be most effective. A higher single-core performance
means that your primary strategy will operate more swiftly. I recommend a
minimum of 4 cores and 16GB of RAM.

While CP-SAT is quite efficient in terms of memory usage, the amount of
available memory can still be a limiting factor in the size of problems you can
tackle. When it came to setting up our lab for extensive benchmarking at TU
Braunschweig, we faced a choice between desktop machines and more expensive
workstations or servers. We chose desktop machines equipped with AMD Ryzen 9
7900 CPUs (Intel would be equally suitable) and 96GB of DDR5 RAM, managed using
Slurm. This decision was driven by the fact that the performance gains from
higher-priced workstations or servers were relatively marginal compared to their
significantly higher costs. When on the road, I am often still able to do stuff
with my old Intel Macbook Pro from 2018 with an i7 and only 16GB of RAM, but
large models will overwhelm it. My workstation at home with AMD Ryzen 7 5700X
and 32GB of RAM on the other hand rarely has any problems with the models I am
working on.

For further guidance, consider the
`hardware recommendations for the Gurobi solver <https://support.gurobi.com/hc/en-us/articles/8172407217041-What-hardware-should-I-select-when-running-Gurobi->`_,
which are likely to be similar. Since we frequently use Gurobi in addition to
CP-SAT, our hardware choices were also influenced by their recommendations.


Example
-------

Before we dive into any internals, let us take a quick look at a simple application of CP-SAT. This example is so simple
that you could solve it by hand, but know that CP-SAT would (probably) be fine with you adding a thousand (maybe even
ten- or hundred-thousand) variables and constraints more.
The basic idea of using CP-SAT is, analogous to MIPs, to define an optimization problem in terms of variables,
constraints, and objective function, and then let the solver find a solution for it.
We call such a formulation that can be understood by the corresponding solver a *model* for the problem.
For people not familiar with this `declarative approach <https://programiz.pro/resources/imperative-vs-declarative-programming/>`_, 
you can compare it to SQL, where you also just state what data you want, not how to get it.
However, it is not purely declarative, because it can still make a huge(!) difference how you model the problem and
getting that right takes some experience and understanding of the internals.
You can still get lucky for smaller problems (let us say a few hundred to thousands of variables) and obtain optimal
solutions without having an idea of what is going on.
The solvers can handle more and more 'bad' problem models effectively with every year.

   **Definition:** A *model* in mathematical programming refers to a mathematical description of a problem, consisting of
   variables, constraints, and optionally an objective function that can be understood by the corresponding solver class.
   *Modelling* refers to transforming a problem (instance) into the corresponding framework, e.g.,
   by making all constraints linear as required for Mixed Integer Linear Programming.
   Be aware that the `SAT <https://en.wikipedia.org/wiki/SAT_solver>`_-community uses the term *model* to refer to a (feasible) 
   variable assignment, i.e., solution of a SAT-formula. If you struggle with this terminology, maybe you want to read
   this short guide on `Math Programming Modelling Basics <https://www.gurobi.com/resources/math-programming-modeling-basics/>`_.

Our first problem has no deeper meaning, except of showing the basic workflow of creating the variables (x and y), adding the
constraint x+y<=30 on them, setting the objective function (maximize 30*x + 50*y), and obtaining a solution:

.. code:: python

   from ortools.sat.python import cp_model

   model = cp_model.CpModel()

   # Variables
   x = model.NewIntVar(0, 100, 'x')  # you always need to specify an upper bound.
   y = model.NewIntVar(0, 100, 'y')
   # there are also no continuous variables: You have to decide for a resolution and then work on integers.

   # Constraints
   model.Add(x + y <= 30)

   # Objective
   model.Maximize(30 * x + 50 * y)

   # Solve
   solver = cp_model.CpSolver()  # Contrary to Gurobi, model and solver are separated.
   status = solver.Solve(model)
   assert status == cp_model.OPTIMAL  # The status tells us if we were able to compute a solution.
   print(f"x={solver.Value(x)},  y={solver.Value(y)}")
   print("=====Stats:======")
   print(solver.SolutionInfo())
   print(solver.ResponseStats())

::

   x=0,  y=30
   =====Stats:======
   default_lp
   CpSolverResponse summary:
   status: OPTIMAL
   objective: 1500
   best_bound: 1500
   booleans: 1
   conflicts: 0
   branches: 1
   propagations: 0
   integer_propagations: 2
   restarts: 1
   lp_iterations: 0
   walltime: 0.00289923
   usertime: 0.00289951
   deterministic_time: 8e-08
   gap_integral: 5.11888e-07

Pretty easy, right? For solving a generic problem, not just one specific instance, you would of course create a
dictionary or list of variables and use something like ``model.Add(sum(vars)<=n)``, because you don't want to create
the model by hand for larger instances.

The output you get may differ from the one above, because CP-SAT actually uses a set of different strategies
in parallel, and just returns the best one (which can differ slightly between multiple runs due to additional randomness).
This is called a portfolio strategy and is a common technique in combinatorial optimization, if you cannot predict
which strategy will perform best.

The mathematical model of the code above would usually be written by experts something like this:

.. math::

   \max 30x + 50y

.. math::

   \text{s.t. } x+y \leq 30

.. math:: 

   \quad 0\leq x \leq 100

.. math::

   \quad 0\leq y \leq 100

.. math:: 

   x,y \in \mathbb{Z}

The ``s.t.`` stands for ``subject to``, sometimes also read as ``such that``.

Here are some further examples, if you are not yet satisfied:

- `N-queens <https://developers.google.com/optimization/cp/queens>`_ (this one
  also gives you a quick introduction to constraint programming, but it may be
  misleading because CP-SAT is no classical
  `FD(Finite Domain)-solver <http://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter26_Rolling_Your_Own_Finite-Domain_Constraint_Solver.pdf>`_.
  This example probably has been modified from the previous generation, which is
  also explained at the end.)
- `Employee Scheduling <https://developers.google.com/optimization/scheduling/employee_scheduling>`_
- `Job Shop Problem <https://developers.google.com/optimization/scheduling/job_shop>`_
- More examples can be found in
  `the official repository <https://github.com/google/or-tools/tree/stable/ortools/sat/samples>`_
  for multiple languages (yes, CP-SAT does support more than just Python). As
  the Python-examples are named in
  `snake-case <https://en.wikipedia.org/wiki/Snake_case>`_, they are at the end of
  the list.

Ok. Now that you have seen a minimal model, let us look on what options we have
to model a problem. Note that an experienced optimizer may be able to model most
problems with just the elements shown above, but showing your intentions may
help CP-SAT optimize your problem better. Contrary to Mixed Integer Programming,
you also do not need to fine-tune any
`Big-Ms <https://en.wikipedia.org/wiki/Big_M_method>`_ (a reason to model
higher-level constraints, such as conditional constraints that are only enforced
if some variable is set to true, in MIPs yourself, because the computer is not
very good at that).

Modelling
---------

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

.. code:: python

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
`./examples/add_no_overlap_2d_scaling.ipynb <./examples/add_no_overlap_2d_scaling.ipynb>`_
for the code. If you have a problem with a lot of continuous variables, such as
`network flow problems <https://en.wikipedia.org/wiki/Network_flow_problem>`_, you
are probably better served with a MIP-solver.

In my experience, boolean variables are by far the most important variables in
many combinatorial optimization problems. Many problems, such as the famous
Traveling Salesman Problem, only consist of boolean variables. Implementing a
solver specialized on boolean variables by using a SAT-solver as a base, such as
CP-SAT, thus, is quite sensible. The resolution of coefficients (in combination
with boolean variables) is less critical than for variables.

You might question the need for naming variables in your model. While it's true
that CP-SAT wouldn't need named variables to work (as it could just give them
automatically generated names), assigning names is incredibly useful for
debugging purposes. Solver APIs often create an internal representation of your
model, which is subsequently used by the solver. There are instances where you
might need to examine this internal model, such as when debugging issues like
infeasibility. In such scenarios, having named variables can significantly
enhance the clarity of the internal representation, making your debugging
process much more manageable.

Objectives
~~~~~~~~~~

Not every problem actually has an objective, sometimes you only need to find a
feasible solution. CP-SAT is pretty good at doing that (MIP-solvers are often
not). However, CP-SAT can also optimize pretty well (older constraint
programming solver cannot, at least in my experience). You can minimize or
maximize a linear expression (use auxiliary variables and constraints to model
more complicated expressions).

You can specify the objective function by calling ``model.Minimize`` or
``model.Maximize`` with a linear expression.

.. code:: python

  model.Maximize(30 * x + 50 * y)

Let us look on how to model more complicated expressions, using boolean
variables and generators.

.. code:: python
  
  x_vars = [model.NewBoolVar(f"x{i}") for i in range(10)]
  model.Minimize(
      sum(i * x_vars[i] if i % 2 == 0 else i * x_vars[i].Not() for i in range(10))
  )


This objective evaluates to

.. math::

  \min \sum_{i=0}^{9} i\cdot x_i \text{ if } i \text{ is even else } i\cdot \neg x_i

To implement a
`lexicographic optimization <https://en.wikipedia.org/wiki/Lexicographic_optimization>`_
you can do multiple rounds and always fix the previous objective as constraint.

.. code:: python

  model.Maximize(30 * x + 50 * y)

  # Lexicographic
  solver.Solve(model)
  model.Add(30 * x + 50 * y == int(solver.ObjectiveValue()))  # fix previous objective
  model.Minimize(z)  # optimize for second objective
  solver.Solve(model)


To implement non-linear objectives, you can use auxiliary variables and
constraints. For example, you can create a variable that is the absolute value
of another variable and then use this variable in the objective.

.. code:: python

  abs_x = model.NewIntVar(0, 100, "|x|")
  model.AddAbsEquality(target=abs_x, expr=x)
  model.Minimize(abs_x)


The available constraints are discussed next.

Linear Constraints
~~~~~~~~~~~~~~~~~~

These are the classical constraints also used in linear optimization. Remember
that you are still not allowed to use floating point numbers within it. Same as
for linear optimization: You are not allowed to multiply a variable with
anything else than a constant and also not to apply any further mathematical
operations.

.. code:: python

  model.Add(10 * x + 15 * y <= 10)
  model.Add(x + z == 2 * y)

  # This one actually isn't linear but still works.
  model.Add(x + y != z)

  # For <, > you can simply use <= and -1 because we are working on integers.
  model.Add(x <= z - 1)  # x < z

Note that ``!=`` can be expected slower than the other (``<=``, ``>=``, ``==``)
constraints, because it is not a linear constraint. If you have a set of
mutually ``!=`` variables, it is better to use ``AllDifferent`` (see below) than to
use the explicit ``!=`` constraints.

.. warning:: 

  If you use intersecting linear constraints, you may get problems
  because the intersection point needs to be integral. There is no such thing as
  a feasibility tolerance as in Mixed Integer Programming-solvers, where small
  deviations are allowed. The feasibility tolerance in MIP-solvers allows, e.g.,
  0.763445 == 0.763439 to still be considered equal to counter numerical issues
  of floating point arithmetic. In CP-SAT, you have to make sure that values can
  match exactly.

Logical Constraints (Propositional Logic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can actually model logical constraints also as linear constraints, but it
may be advantageous to show your intent:

.. code:: python

  b1 = model.NewBoolVar("b1")
  b2 = model.NewBoolVar("b2")
  b3 = model.NewBoolVar("b3")

  model.AddBoolOr(b1, b2, b3)  # b1 or b2 or b3 (at least one)
  model.AddBoolAnd(b1, b2.Not(), b3.Not())  # b1 and not b2 and not b3 (all)
  model.AddBoolXOr(b1, b2, b3)  # b1 xor b2 xor b3
  model.AddImplication(b1, b2)  # b1 -> b2


In this context you could also mention ``AddAtLeastOne``, ``AddAtMostOne``, and
``AddExactlyOne``, but these can also be modelled as linear constraints.

Conditional Constraints
~~~~~~~~~~~~~~~~~~~~~~~

Linear constraints (Add), BoolOr, and BoolAnd support being activated by a
condition. This is not only a very helpful constraint for many applications, but
it is also a constraint that is highly inefficient to model with linear
optimization (`Big M Method <https://en.wikipedia.org/wiki/Big_M_method>`_). My
current experience shows that CP-SAT can work much more efficiently with this
kind of constraint. Note that you only can use a boolean variable and not
directly add an expression, i.e., maybe you need to create an auxiliary
variable.

.. code:: python

  model.Add(x + z == 2 * y).OnlyEnforceIf(b1)
  model.Add(x + z == 10).OnlyEnforceIf([b2, b3.Not()])  # only enforce if b2 AND NOT b3

AllDifferent
~~~~~~~~~~~~

A constraint that is often seen in Constraint Programming, but I myself was
always able to deal without it. Still, you may find it important. It forces all
(integer) variables to have a different value.

``AllDifferent`` is actually the only constraint that may use a domain based
propagator (if it is not a permutation)
[`source <https://youtu.be/lmy1ddn4cyw?t=624>`_]

.. code:: python

  model.AddAllDifferent(x, y, z)

  # You can also add a constant to the variables.
  vars = [model.NewIntVar(0, 10) for i in range(10)]
  model.AddAllDifferent(x + i for i, x in enumerate(vars))

The `N-queens <https://developers.google.com/optimization/cp/queens>`_ example of
the official tutorial makes use of this constraint.

There is a big caveat with this constraint: CP-SAT now has a preprocessing step
that automatically tries to infer large ``AllDifferent`` constraints from sets of
mutual ``!=`` constraints. This inference equals the NP-hard Edge Clique Cover
problem, thus, is not a trivial task. If you add an ``AllDifferent`` constraint
yourself, CP-SAT will assume that you already took care of this inference and
will skip this step. Thus, adding a single ``AllDifferent`` constraint can make
your model significantly slower, if you also use ``!=`` constraints. If you do not
use ``!=`` constraints, you can safely use ``AllDifferent`` without any performance
penalty. You may also want to use ``!=`` instead of ``AllDifferent`` if you apply it
to overlapping sets of variables without proper optimization, because then
CP-SAT will do the inference for you.

In `./examples/add_all_different.ipynb <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_all_different.ipynb>`_ you
can find a quick experiment based on the graph coloring problem. In the graph
coloring problem, the colors of two adjacent vertices have to be different. This
can be easily modelled by ``!=`` or ``AllDifferent`` constraints on every edge.
Using ``!=``, we can solve the example graph in around 5 seconds. If we use
``AllDifferent``, it takes more than 5 minutes. If we manually disable the
``AllDifferent`` inference, it also takes more than 5 minutes. Same if we add just
a single ``AllDifferent`` constraint. Thus, if you use ``AllDifferent`` do it
properly on large sets, or use ``!=`` constraints and let CP-SAT infer the
``AllDifferent`` constraints for you.

Maybe CP-SAT will allow you to use ``AllDifferent`` without any performance
penalty in the future, but for now, you have to be aware of this. See also
`the optimization parameter documentation <https://github.com/google/or-tools/blob/1d696f9108a0ebfd99feb73b9211e2f5a6b0812b/ortools/sat/sat_parameters.proto#L542>`_.

Absolute Values and Max/Min
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two often occurring and important operators are absolute values as well as
minimum and maximum values. You cannot use operators directly in the
constraints, but you can use them via an auxiliary variable and a dedicated
constraint. These constraints are reasonably efficient in my experience.

.. code:: python

  # abs_xz == |x+z|
  abs_xz = model.NewIntVar(0, 200, "|x+z|")  # ub = ub(x)+ub(z)
  model.AddAbsEquality(target=abs_xz, expr=x + z)
  # max_xyz = max(x,y,z)
  max_xyz = model.NewIntVar(0, 100, "max(x,y, z)")
  model.AddMaxEquality(max_xyz, [x, y, z])
  # min_xyz = min(x,y,z)
  min_xyz = model.NewIntVar(-100, 100, " min(x,y, z)")
  model.AddMinEquality(min_xyz, [x, y, z])

Multiplication and Modulo
~~~~~~~~~~~~~~~~~~~~~~~~~

A big nono in linear optimization (the most successful optimization area) are
multiplication of variables (because this would no longer be linear, right...).
Often we can linearize the model by some tricks and tools like Gurobi are also
able to do some non-linear optimization ( in the end, it is most often
translated to a less efficient linear model again). CP-SAT can also work with
multiplication and modulo of variables, again as constraint not as operation. So
far, I have not made good experience with these constraints, i.e., the models
end up being slow to solve, and would recommend to only use them if you really
need them and cannot find a way around them.

.. code:: python

  xyz = model.NewIntVar(-100 * 100 * 100, 100**3, "x*y*z")
  model.AddMultiplicationEquality(xyz, [x, y, z])  # xyz = x*y*z
  model.AddModuloEquality(x, y, 3)  # x = y % 3

.. warning:: 

  The documentation indicates that multiplication of more than two
  variables is supported, but I got an error when trying it out. I have not
  investigated this further, as I would expect it to be slow anyway.

Circuit/Tour-Constraints
~~~~~~~~~~~~~~~~~~~~~~~~

The
`Traveling Salesman Problem (TSP) <https://en.wikipedia.org/wiki/Travelling_salesman_problem>`_
or Hamiltonicity Problem are important and difficult problems that occur as
subproblem in many contexts. For solving the classical TSP, you should use the
extremely powerful solver
`Concorde <https://www.math.uwaterloo.ca/tsp/concorde.html>`_. There is also a
separate `part in ortools <https://developers.google.com/optimization/routing>`_
dedicated to routing. If it is just a subproblem, you can add a simple
constraint by encoding the allowed edges as triples of start vertex index,
target vertex index, and literal/variable. Note that this is using directed
edges/arcs. By adding a triple (v,v,var), you can allow CP-SAT to skip the
vertex v.

  If the tour-problem is the fundamental part of your problem, you may be better
  served with using a Mixed Integer Programming solver. Don't expect to solve
  tours much larger than 250 vertices with CP-SAT.

.. code:: python

  from ortools.sat.python import cp_model

  # Weighted, directed graph as instance
  # (source, destination) -> cost
  dgraph = {
      (0, 1): 13,
      (1, 0): 17,
      (1, 2): 16,
      (2, 1): 19,
      (0, 2): 22,
      (2, 0): 14,
      (3, 0): 15,
      (3, 1): 28,
      (3, 2): 25,
      (0, 3): 24,
      (1, 3): 11,
      (2, 3): 27,
  }
  model = cp_model.CpModel()
  # Variables: Binary decision variables for the edges
  edge_vars = {(u, v): model.NewBoolVar(f"e_{u}_{v}") for (u, v) in dgraph.keys()}
  # Constraints: Add Circuit constraint
  # We need to tell CP-SAT which variable corresponds to which edge.
  # This is done by passing a list of tuples (u,v,var) to AddCircuit.
  circuit = [
      (u, v, var) for (u, v), var in edge_vars.items()  # (source, destination, variable)
  ]
  model.AddCircuit(circuit)

  # Objective: minimize the total cost of edges
  obj = sum(dgraph[(u, v)] * x for (u, v), x in edge_vars.items())
  model.Minimize(obj)

  # Solve
  solver = cp_model.CpSolver()
  status = solver.Solve(model)
  assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
  tour = [(u, v) for (u, v), x in edge_vars.items() if solver.Value(x)]
  print("Tour:", tour)

::

  Tour: [(0, 1), (2, 0), (3, 2), (1, 3)]

You can use this constraint very flexibly for many tour problems. We added three
examples:

- `./examples/add_circuit.py <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_circuit.py>`_: The example above,
  slightly extended. Find out how large you can make the graph.
- `./examples/add_circuit_budget.py <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_circuit_budget.py>`_: Find the
  largest tour with a given budget. This will be a bit more difficult to solve.
- `./examples/add_circuit_multi_tour.py <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_circuit_multi_tour.py>`_:
  Allow :math:`k` tours, which in sum need to be minimal and cover all vertices.

The most powerful TSP-solver *concorde* uses a linear programming based
approach, but with a lot of additional techniques to improve the performance.
The book *In Pursuit of the Traveling Salesman* by William Cook may have already
given you some insights. For more details, you can also read the more advanced
book *The Traveling Salesman Problem: A Computational Study* by Applegate,
Bixby, Chvatál, and Cook. If you need to solve some variant, MIP-solvers (which
could be called a generalization of that approach) are known to perform well
using the
`Dantzig-Fulkerson-Johnson Formulation <https://en.wikipedia.org/wiki/Travelling_salesman_problem#Dantzig%E2%80%93Fulkerson%E2%80%93Johnson_formulation>`_.
This model is theoretically exponential, but using lazy constraints (which are
added when needed), it can be solved efficiently in practice. The
`Miller-Tucker-Zemlin formulation <https://en.wikipedia.org/wiki/Travelling_salesman_problem#Miller%E2%80%93Tucker%E2%80%93Zemlin_formulation[21]>`_
allows a small formulation size, but is bad in practice with MIP-solvers due to
its weak linear relaxations. Because CP-SAT does not allow lazy constraints, the
Danzig-Fulkerson-Johnson formulation would require many iterations and a lot of
wasted resources. As CP-SAT does not suffer as much from weak linear relaxations
(replacing Big-M by logic constraints, such as ``OnlyEnforceIf``), the
Miller-Tucker-Zemlin formulation may be an option in some cases, though a simple
experiment (see below) shows a similar performance as the iterative approach.
When using ``AddCircuit``, CP-SAT will actually use the LP-technique for the
linear relaxation (so using this constraint may really help, as otherwise CP-SAT
will not know that your manual constraints are actually a tour with a nice
linear relaxation), and probably has the lazy constraints implemented
internally. Using the ``AddCircuit`` constraint is thus highly recommendable for
any circle or path constraints.

In
`./examples/add_circuit_comparison.ipynb <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_circuit_comparison.ipynb>`_,
we compare the performance of some models for the TSP, to estimate the
performance of CP-SAT for the TSP.

- **AddCircuit** can solve the Euclidean TSP up to a size of around 110 vertices
  in 10 seconds to optimality.
- **MTZ (Miller-Tucker-Zemlin)** can solve the eculidean TSP up to a size of
  around 50 vertices in 10 seconds to optimality.
- **Dantzig-Fulkerson-Johnson via iterative solving** can solve the eculidean
  TSP up to a size of around 50 vertices in 10 seconds to optimality.
- **Dantzig-Fulkerson-Johnson via lazy constraints in Gurobi** can solve the
  eculidean TSP up to a size of around 225 vertices in 10 seconds to optimality.

This tells you to use a MIP-solver for problems dominated by the tour
constraint, and if you have to use CP-SAT, you should definitely use the
``AddCircuit`` constraint.

  These are all naive implementations, and the benchmark is not very rigorous.
  These values are only meant to give you a rough idea of the performance.
  Additionally, this benchmark was regarding proving *optimality*. The
  performance in just optimizing a tour could be different. The numbers could
  also look different for differently generated instances. You can find a more
  detailed benchmark in the later section on proper evaluation.

Here is the performance of ``AddCircuit`` for the TSP on some instances (rounded
eucl. distance) from the TSPLIB with a time limit of 90 seconds.

+----------+---------+---------+-------------+-----------+----------+
| Instance | # nodes | runtime | lower bound | objective | opt. gap |
+==========+=========+=========+=============+===========+==========+
| att48    |      48 |    0.47 |       33522 |     33522 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| eil51    |      51 |    0.69 |         426 |       426 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| st70     |      70 |     0.8 |         675 |       675 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| eil76    |      76 |    2.49 |         538 |       538 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr76     |      76 |   54.36 |      108159 |    108159 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroD100  |     100 |    9.72 |       21294 |     21294 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroC100  |     100 |    5.57 |       20749 |     20749 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroB100  |     100 |     6.2 |       22141 |     22141 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroE100  |     100 |    9.06 |       22049 |     22068 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroA100  |     100 |    8.41 |       21282 |     21282 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| eil101   |     101 |    2.24 |         629 |       629 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| lin105   |     105 |    1.37 |       14379 |     14379 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr107    |     107 |     1.2 |       44303 |     44303 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr124    |     124 |    33.8 |       59009 |     59030 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr136    |     136 |   35.98 |       96767 |     96861 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr144    |     144 |   21.27 |       58534 |     58571 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroB150  |     150 |   58.44 |       26130 |     26130 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroA150  |     150 |   90.94 |       26498 |     26977 |       2% |
+----------+---------+---------+-------------+-----------+----------+
| pr152    |     152 |   15.28 |       73682 |     73682 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| kroA200  |     200 |   90.99 |       29209 |     29459 |       1% |
+----------+---------+---------+-------------+-----------+----------+
| kroB200  |     200 |   31.69 |       29437 |     29437 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| pr226    |     226 |   74.61 |       80369 |     80369 |        0 |
+----------+---------+---------+-------------+-----------+----------+
| gil262   |     262 |   91.58 |        2365 |      2416 |       2% |
+----------+---------+---------+-------------+-----------+----------+
| pr264    |     264 |   92.03 |       49121 |     49512 |       1% |
+----------+---------+---------+-------------+-----------+----------+
| pr299    |     299 |   92.18 |       47709 |     49217 |       3% |
+----------+---------+---------+-------------+-----------+----------+
| linhp318 |     318 |   92.45 |       41915 |     52032 |      19% |
+----------+---------+---------+-------------+-----------+----------+
| lin318   |     318 |   92.43 |       41915 |     52025 |      19% |
+----------+---------+---------+-------------+-----------+----------+
| pr439    |     439 |   94.22 |      105610 |    163452 |      35% |
+----------+---------+---------+-------------+-----------+----------+

Array operations
~~~~~~~~~~~~~~~~

You can even go completely bonkers and work with arrays in your model. The
element at a variable index can be accessed via an ``AddElement`` constraint.

The second constraint is actually more of a stable matching in array form. For
two arrays of variables :math:`v,w, |v|=|w|`, it requires
:math:`v[i]=j \Leftrightarrow w[j]=i \quad \forall i,j \in 0,\ldots,|v|-1`. Note that
this restricts the values of the variables in the arrays to :math:`0,\ldots, |v|-1`.

.. code:: python

  # ai = [x,y,z][i]  assign ai the value of the i-th entry.
  ai = model.NewIntVar(-100, 100, "a[i]")
  i = model.NewIntVar(0, 2, "i")
  model.AddElement(index=i, variables=[x, y, z], target=ai)

  model.AddInverse([x, y, z], [z, y, x])

Interval Variables and No-Overlap Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CP-SAT also supports interval variables and corresponding constraints. These are
important for scheduling and packing problems. There are simple no-overlap
constraints for intervals for one-dimensional and two-dimensional intervals. In
two-dimensional intervals, only one dimension is allowed to overlap, i.e., the
other dimension has to be disjoint. This is essentially rectangle packing. Let
us see how we can model a simple 2-dimensional packing problem. Note that
``NewIntervalVariable`` may indicate a new variable, but it is actually a
constraint container in which you have to insert the classical integer
variables. This constraint container is required, e.g., for the no-overlap
constraint.

.. code:: python

  from ortools.sat.python import cp_model

  # Instance
  container = (40, 15)
  boxes = [
      (11, 3),
      (13, 3),
      (9, 2),
      (7, 2),
      (9, 3),
      (7, 3),
      (11, 2),
      (13, 2),
      (11, 4),
      (13, 4),
      (3, 5),
      (11, 2),
      (2, 2),
      (11, 3),
      (2, 3),
      (5, 4),
      (6, 4),
      (12, 2),
      (1, 2),
      (3, 5),
      (13, 5),
      (12, 4),
      (1, 4),
      (5, 2),
      # (6,  2),  # add to make tight
      # (6,3), # add to make infeasible
  ]
  model = cp_model.CpModel()

  # We have to create the variable for the bottom left corner of the boxes.
  # We directly limit their range, such that the boxes are inside the container
  x_vars = [
      model.NewIntVar(0, container[0] - box[0], name=f"x1_{i}")
      for i, box in enumerate(boxes)
  ]
  y_vars = [
      model.NewIntVar(0, container[1] - box[1], name=f"y1_{i}")
      for i, box in enumerate(boxes)
  ]
  # Interval variables are actually more like constraint containers, that are then passed to the no overlap constraint
  # Note that we could also make size and end variables, but we don't need them here
  x_interval_vars = [
      model.NewIntervalVar(
          start=x_vars[i], size=box[0], end=x_vars[i] + box[0], name=f"x_interval_{i}"
      )
      for i, box in enumerate(boxes)
  ]
  y_interval_vars = [
      model.NewIntervalVar(
          start=y_vars[i], size=box[1], end=y_vars[i] + box[1], name=f"y_interval_{i}"
      )
      for i, box in enumerate(boxes)
  ]
  # Enforce that no two rectangles overlap
  model.AddNoOverlap2D(x_interval_vars, y_interval_vars)

  # Solve!
  solver = cp_model.CpSolver()
  solver.parameters.log_search_progress = True
  solver.log_callback = print
  status = solver.Solve(model)
  assert status == cp_model.OPTIMAL
  for i, box in enumerate(boxes):
      print(
          f"box {i} is placed at ({solver.Value(x_vars[i])}, {solver.Value(y_vars[i])})"
      )

.. note:: 

  The keywords ``start`` may be named ``begin`` in some versions of ortools.

See `this notebook <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_no_overlap_2d.ipynb>`_ for the full example.

There is also the option for optional intervals, i.e., intervals that may be
skipped. This would allow you to have multiple containers or do a knapsack-like
packing.

The resolution seems to be quite important for this problem, as mentioned
before. The following table shows the runtime for different resolutions (the
solution is always the same, just scaled).

+------------+---------+
| Resolution | Runtime |
+============+=========+
| 1x         | 0.02s   |
+------------+---------+
| 10x        | 0.7s    |
+------------+---------+
| 100x       | 7.6s    |
+------------+---------+
| 1000x      | 75s     |
+------------+---------+
| 10_000x    | >15min  |
+------------+---------+

See `this notebook <https://github.com/d-krupke/cpsat-primer/blob/main/examples/add_no_overlap_2d_scaling.ipynb>`_ for the full
example.

However, while playing around with less documented features, I noticed that the
performance can be improved drastically with the following parameters:

.. code:: python

  solver.parameters.use_energetic_reasoning_in_no_overlap_2d = True
  solver.parameters.use_timetabling_in_no_overlap_2d = True
  solver.parameters.use_pairwise_reasoning_in_no_overlap_2d = True

Instances that could not be solved in 15 minutes before, can now be solved in
less than a second. This of course does not apply for all instances, but if you
are working with this constraint, you may want to jiggle with these parameters
if it struggles with solving your instances.

There is more
~~~~~~~~~~~~~
CP-SAT has even more constraints, but I think I covered the most important ones.
If you need more, you can check out the
`official documentation <https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel>`_.


