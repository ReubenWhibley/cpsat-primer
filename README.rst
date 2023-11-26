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

