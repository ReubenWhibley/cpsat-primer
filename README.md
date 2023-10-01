# Using and Understanding ortools' CP-SAT: A Primer and Cheat Sheet

*By Dominik Krupke, TU Braunschweig*

**This tutorial is under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Smaller parts can be copied without
any acknowledgement for non-commercial, educational purposes. Contributions are very welcome, even if it is just spell-checking.**

> :warning: **You are reading a draft! Expect lots of mistakes (and please report them either as an issue or pull request :) )**

Many [combinatorially difficult](https://en.wikipedia.org/wiki/NP-hardness) optimization problems can, despite their proved theoretical hardness, be solved reasonably well in practice.
The most successful approach is to use [Mixed Integer Linear Programming](https://en.wikipedia.org/wiki/Integer_programming) (MIP) to model the problem and then use a solver to find a solution.
The most successful solvers for MIPs are [Gurobi](https://www.gurobi.com/) and [CPLEX](https://www.ibm.com/analytics/cplex-optimizer), which are both commercial and expensive (though, free for academics).
There are also some open source solvers, but they are often not as powerful as the commercial ones.
However, even when investing in such a solver, the underlying techniques ([Branch and Bound](https://en.wikipedia.org/wiki/Branch_and_bound)
& [Cut](https://en.wikipedia.org/wiki/Branch_and_cut) on [Linear Relaxations](https://en.wikipedia.org/wiki/Linear_programming_relaxation)) struggle with some optimization problems, especially if the problem contains a lot of logical constraints that a solution has to satisfy.
In this case, the [Constraint Programming](https://en.wikipedia.org/wiki/Constraint_programming) (CP) approach may be more successful.
For Constraint Programming, there are many open source solvers, but they are often not as powerful as the commercial MIP-solvers.
While MIP-solvers are frequently able to solve problems with hundreds of thousands of variables and constraints, the classical CP-solvers often struggle with problems with more than a few thousand variables and constraints.
However, the relatively new [CP-SAT](https://developers.google.com/optimization/cp/cp_solver) of Google's [ortools](https://github.com/google/or-tools/)
suite shows to overcome many of the weaknesses and provides a viable alternative to MIP-solvers, being competitive for many problems and sometimes even superior.

This unofficial primer shall help you use and understand this powerful tool, especially if you are coming from
the [Mixed Integer Linear Programming](https://en.wikipedia.org/wiki/Integer_programming) -community, as
it may prove useful in cases where Branch and Bound performs poorly.

If you are relatively new to combinatorial optimization, I suggest you to read the relatively short book [In Pursuit of the Traveling Salesman by Bill Cook](https://press.princeton.edu/books/paperback/9780691163529/in-pursuit-of-the-traveling-salesman) first.
It tells you a lot about the history and techniques to deal with combinatorial optimization problems, on the example of the famous [Traveling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem).
The Traveling Salesman Problem seems to be intractable already for small instances, but it is actually possible to solve instances with thousands of cities in practice.
It is a very light read and you can skip the more technical parts if you want to.
As an alternative, you can also read this [free chapter, coauthored by the same author](https://www.math.uwaterloo.ca/~bico/papers/comp_chapter1.pdf) and 
watch this very amusing [YouTube Video (1hour)](https://www.youtube.com/watch?v=5VjphFYQKj8).
If you are short on time, at least watch the video, it is really worth it.
While CP-SAT follows a slightly different approach than the one described in the book/chapter/video, it is still important to see why it is possible to do the seemingly impossible and solve such problems in practice, despite their theoretical hardness.
Additionally, you will have learned the concept of [Mathematical Programming](https://www.gurobi.com/resources/math-programming-modeling-basics/), and know that the term "Programming" has nothing to do with programming in the sense of writing code (otherwise, additionally read the just given reference).

After that (or if you are already familiar with combinatorial optimization), the following content awaits you in this primer:

**Content:**

1. [Installation](#installation): Quick installation guide.
2. [Example](#example): A short example, showing the usage of CP-SAT.
3. [Modelling](#modelling): An overview of variables, objectives, and constraints. The constraints make the most
   important part.
4. [Parameters](#parameters): How to specify CP-SATs behavior, if needed. Timelimits, hints, assumptions,
   parallelization, ...
5. [How does it work?](#how-does-it-work): After we know what we can do with CP-SAT, we look into how CP-SAT will do all
   these things.
6. [Large Neighborhood Search](#large-neighborhood-search): The use of CP-SAT to create more powerful heuristics.
7. [Further Material](#further-material): Some more resources if you want to dig deeper.

> **Target audience:** People (especially my students at TU Braunschweig) with some background
> in [integer programming](https://en.wikipedia.org/wiki/Integer_programming)
> /[linear optimization](https://en.wikipedia.org/wiki/Linear_programming), who would like to know an actual viable
> alternative to [Branch and Cut](https://en.wikipedia.org/wiki/Branch_and_cut). However, I try to make it
> understandable for anyone interested
> in [combinatorial optimization](https://en.wikipedia.org/wiki/Combinatorial_optimization).

> **About the (main) author:**
> [Dr. Dominik Krupke](https://krupke.cc) is a postdoctoral researcher at the [Algorithms Group](https://www.ibr.cs.tu-bs.de/alg) at TU Braunschweig,
>  where he researches and teaches on how to solve NP-hard problems in practice. He started writing this primer as course material for his students,
>  but continued and extended it (mostly in his spare time) to make it available to a wider audience.



## Installation

We are using Python 3 in this primer and assume that you have a working Python 3 installation as well as the basic knowledge to use it.
There are also interfaces for other languages, but Python 3 is, in my opinion, the most convenient one, as the mathematical
expressions in Python are very close to the mathematical notation (allowing you to spot mathmetical errors much faster).
Only for huge models, you may need to use a compiled language such as C++ due to performance issues.
For smaller models, you will not notice any performance difference.

The installation of CP-SAT, which is part of the ortools package, is very easy and can
be done via Python's package manager [pip](https://pip.pypa.io/en/stable/).

```shell
pip3 install -U ortools
```

This command will also update an existing installation of ortools.
As this tool is in active development, it is recommendable to update it frequently.
We actually encountered wrong behavior, i.e., bugs, in earlier versions that then have
been fixed by updates (this was on some more advanced features, don't worry about
correctness with basic usage).

I personally like to use [Jupyter Notebooks](https://jupyter.org/) for experimenting with CP-SAT.

## Example

Before we dive into any internals, let us take a quick look at a simple application of CP-SAT. This example is so simple
that you could solve it by hand, but know that CP-SAT would (probably) be fine with you adding a thousand (maybe even
ten- or hundred-thousand) variables and constraints more.
The basic idea of using CP-SAT is, analogous to MIPs, to define an optimization problem in terms of variables,
constraints, and objective function, and then let the solver find a solution for it.
We call such a formulation that can be understood by the corresponding solver a *model* for the problem.
For people not familiar with this [declarative approach](https://programiz.pro/resources/imperative-vs-declarative-programming/), you can compare it to SQL, where you also just state what data
you want, not how to get it.
However, it is not purely declarative, because it can still make a huge(!) difference how you model the problem and
getting that right takes some experience and understanding of the internals.
You can still get lucky for smaller problems (let us say a few hundred to thousands of variables) and obtain optimal
solutions without having an idea of what is going on.
The solvers can handle more and more 'bad' problem models effectively with every year.

> **Definition:** A *model* in mathematical programming refers to a mathematical description of a problem, consisting of
> variables, constraints, and optionally an objective function that can be understood by the corresponding solver class.
> *Modelling* refers to transforming a problem (instance) into the corresponding framework, e.g.,
> by making all constraints linear as required for Mixed Integer Linear Programming.
> Be aware that the [SAT](https://en.wikipedia.org/wiki/SAT_solver)-community uses the term *model* to refer to a (feasible) 
> variable assignment, i.e., solution of a SAT-formula. If you struggle with this terminology, maybe you want to read
> this short guide on [Math Programming Modelling Basics](https://www.gurobi.com/resources/math-programming-modeling-basics/).

Our first problem has no deeper meaning, except of showing the basic workflow of creating the variables (x and y), adding the
constraint x+y<=30 on them, setting the objective function (maximize 30*x + 50*y), and obtaining a solution:

```python
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
```

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
dictionary or list of variables and use something like `model.Add(sum(vars)<=n)`, because you don't want to create
the model by hand for larger instances.

The output you get may differ from the one above, because CP-SAT actually uses a set of different strategies
in parallel, and just returns the best one (which can differ slightly between multiple runs due to additional randomness).
This is called a portfolio strategy and is a common technique in combinatorial optimization, if you cannot predict
which strategy will perform best.

The mathematical model of the code above would usually be written by experts something like this:

```math
\max 30x + 50y
```
```math
\text{s.t. } x+y \leq 30
```
```math
\quad 0\leq x \leq 100
```
```math
\quad 0\leq y \leq 100
```
```math
x,y \in \mathbb{Z}
```

The `s.t.` stands for `subject to`, sometimes also read as `such that`.

Here are some further examples, if you are not yet satisfied:

* [N-queens](https://developers.google.com/optimization/cp/queens) (this one also gives you a quick introduction to
  constraint programming, but it may be misleading because CP-SAT is no classical [FD(Finite Domain)-solver](http://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter26_Rolling_Your_Own_Finite-Domain_Constraint_Solver.pdf). This example probably has
  been modified from the previous generation, which is also explained at the end.)
* [Employee Scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling)
* [Job Shop Problem](https://developers.google.com/optimization/scheduling/job_shop)
* More examples can be found
  in [the official repository](https://github.com/google/or-tools/tree/stable/ortools/sat/samples) for multiple
  languages (yes, CP-SAT does support more than just Python). As the Python-examples are named in [snake-case](https://en.wikipedia.org/wiki/Snake_case), they are
  at the end of the list.

Ok. Now that you have seen a minimal model, let us look on what options we have to model a problem. Note that an
experienced optimizer may be able to model most problems with just the elements shown above, but showing your intentions
may help CP-SAT optimize your problem better. Contrary to Mixed Integer Programming, you also do not need to fine-tune
any [Big-Ms](https://en.wikipedia.org/wiki/Big_M_method) (a reason to model higher-level constraints, such as conditional constraints that are only enforced if some variable is set to true, in MIPs yourself, because the computer is not very good at that).



---

## Modelling

CP-SAT provides us with much more modelling options than the classical MIP-solver.
Instead of just the classical linear constraints (<=, ==, >=), we have various advanced constraints
such as `AllDifferent` or `AddMultiplicationEquality`. This spares you the burden
of modelling the logic only with linear constraints, but also makes the interface
more extensive. Additionally, you have to be aware that not all constraints are
equally efficient. The most efficient constraints are linear or boolean constraints.
Constraints such as `AddMultiplicationEquality` can be significantly(!!!) more expensive.

> __If you are coming from the MIP-world, you should not overgeneralize your experience__
> to CP-SAT as the underlying techniques are different. It does not rely on the linear
> relaxation as much as MIP-solvers do. Thus, you can often use modelling techniques that are
> not efficient in MIP-solvers, but perform reasonably well in CP-SAT. For example,
> I had a model that required multiple absolute values and performed significantly
> better in CP-SAT than in Gurobi (despite a manual implementation with relatively
> tight big-M values).

This primer does not have the space to teach about building good models.
In the following, we will primarily look onto a selection of useful constraints.
If you want to learn how to build models, you could take a look into the book
[Model Building in Mathematical Programming by H. Paul Williams](https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330)
which covers much more than you probably need, including some actual applications. 
This book is of course not for CP-SAT, but the general techniques and ideas carry over.
However, it can also suffice to simply look on some other models and try some things out.
If you are completely new to this area, you may want to check out modelling for the MIP-solver Gurobi in this [video course](https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9).
Remember that many things are similar to CP-SAT, but not everything (as already mentioned, CP-SAT is especially interesting for the cases where a MIP-solver fails).

The following part does not cover all constraints. You can get a complete overview by looking into the 
[official documentation](https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel).
Simply go to `CpModel` and check out the `AddXXX` and `NewXXX` methods.

Resources on mathematical modelling (not CP-SAT specific):

* [Math Programming Modeling Basics by Gurobi](https://www.gurobi.com/resources/math-programming-modeling-basics/): Get the absolute basics.
* [Modeling with Gurobi Python](https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9): A video course on modelling with Gurobi. The concepts carry over to CP-SAT.
* [Model Building in Mathematical Programming by H. Paul Williams](https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330): A complete book on mathematical modelling.

### Variables

There are two important types of variables in CP-SAT: Booleans and Integers (which are actually converted to Booleans, but more on this later).
There are also, e.g., [interval variables](https://developers.google.com/optimization/reference/python/sat/python/cp_model#intervalvar),
but they are not as important and can be modelled easily with integer variables.
For the integer variables, you have to specify a lower and an upper bound.

```python
# integer variable z with bounds -100 <= z <= 100
z = model.NewIntVar(-100, 100, 'z')
# boolean variable b
b = model.NewBoolVar('b')
# implicitly available negation of b:
not_b = b.Not()  # will be 1 if b is 0 and 0 if b is 1
```

> Having tight bounds on the integer variables can make a huge impact on the performance.
> It may be useful to run some optimization heuristics beforehand to get some bounds.
> Reducing it by a few percent can already pay off for some problems.

There are no continuous/floating point variables (or even constants) in CP-SAT: If you need floating point numbers, you have to
approximate them with integers by some resolution.
For example, you could simply multiply all values by 100 for a step size of 0.01.
A value of 2.35 would then be represented by 235.
This *could* probably be implemented in CP-SAT directly, but doing it explicitly is not difficult, and it has
numerical implications that you should be aware of.

The lack of continuous variables may sound like a serious limitation,
especially if you have a background in linear optimization (where continuous variables are the "easy part"),
but as long as they are not a huge part of your problem, you can often work around it.
I had problems with many continuous variables on which I had to apply absolute values and conditional linear constraints, and
CP-SAT performed much better than Gurobi, which is known to be very good at continuous variables.
In this case, CP-SAT struggled less with the continuous variables (Gurobi's strength), than Gurobi with the logical constraints (CP-SAT's strength).
In a further analysis, I noted an only logarithmic increase of the runtime with the resolution.
However, there are also problems for which a higher resolution can drastically increase the runtime.
The packing problem, which is discussed further below, has the following runtime for different resolutions:
1x: 0.02s, 10x: 0.7s, 100x: 7.6s, 1000x: 75s, 10_000x: >15min.
The solution was always the same, just scaled, and there was no objective, i.e., only a feasible solution had to be found.
Note that this is just an example, not a representative benchmark.
See [./examples/add_no_overlap_2d_scaling.ipynb](./examples/add_no_overlap_2d_scaling.ipynb) for the code.
If you have a problem with a lot of continuous variables, such as [network flow problems](https://en.wikipedia.org/wiki/Network_flow_problem), you are probably better served with a MIP-solver.

In my experience, boolean variables are by far the most important variables in many combinatorial optimization problems.
Many problems, such as the famous Traveling Salesman Problem, only consist of boolean variables.
Implementing a solver specialized on boolean variables by using a SAT-solver as a base, such as CP-SAT, thus, is quite sensible.
The resolution of coefficients (in combination with boolean variables) is less critical than for variables.


### Objectives

Not every problem actually has an objective, sometimes you only need to find a feasible solution.
CP-SAT is pretty good at doing that (MIP-solvers are often not).
However, CP-SAT can also optimize pretty well (older constraint programming solver cannot, at least in my experience). You
can minimize or maximize a linear expression (use auxiliary variables and constraints to model more complicated expressions). 

You can specify the objective function by calling `model.Minimize` or `model.Maximize` with a linear expression.
```python
model.Maximize(30 * x + 50 * y)
```

Let us look on how to model more complicated expressions, using boolean variables and generators.
```python
x_vars = [model.NewBoolVar(f'x{i}') for i in range(10)]
model.Minimize(sum(i*x_vars[i] if i%2==0 else i*x_vars[i].Not() for i in range(10)))
```
This objective evaluates to
```math
\min \sum_{i=0}^{9} i\cdot x_i \text{ if } i \text{ is even else } i\cdot \neg x_i
```

To implement a
[lexicographic optimization](https://en.wikipedia.org/wiki/Lexicographic_optimization), 
you can do multiple rounds and always fix the previous objective as constraint.

```python
model.Maximize(30 * x + 50 * y)

# Lexicographic
solver.Solve(model)
model.Add(30 * x + 50 * y == int(solver.ObjectiveValue()))  # fix previous objective
model.Minimize(z)  # optimize for second objective
solver.Solve(model)
```

To implement non-linear objectives, you can use auxiliary variables and constraints.
For example, you can create a variable that is the absolute value of another variable and then use this variable in the
objective.

```python
abs_x = model.NewIntVar(0, 100, "|x|")
model.AddAbsEquality(target=abs_x, expr=x)
model.Minimize(abs_x)
```

The available constraints are discussed next.

### Linear Constraints

These are the classical constraints also used in linear optimization.
Remember that you are still not allowed to use floating point numbers within it.
Same as for linear optimization: You are not allowed to multiply a variable with anything else than a constant and also
not to apply any further mathematical operations.

```python
model.Add(10 * x + 15 * y <= 10)
model.Add(x + z == 2 * y)

# This one actually isn't linear but still works.
model.Add(x + y != z)

# For <, > you can simply use <= and -1 because we are working on integers.
model.Add(x <= z - 1)  # x < z
```

Note that `!=` can be expected slower than the other (`<=`, `>=`, `==`) constraints, because it is not a linear constraint.
If you have a set of mutually `!=` variables, it is better to use `AllDifferent` (see below) than to use the explicit `!=` constraints.

> :warning: If you use intersecting linear constraints, you may get problems because the intersection point needs to
> be integral. There is no such thing as a feasibility tolerance as in Mixed Integer Programming-solvers, where small deviations
> are allowed. The feasibility tolerance in MIP-solvers allows, e.g., 0.763445 == 0.763439 to still be considered equal to counter
> numerical issues of floating point arithmetic. In CP-SAT, you have to make sure that values can match exactly.

### Logical Constraints (Propositional Logic)

You can actually model logical constraints also as linear constraints, but it may be advantageous to show your intent:

```python
b1 = model.NewBoolVar('b1')
b2 = model.NewBoolVar('b2')
b3 = model.NewBoolVar('b3')

model.AddBoolOr(b1, b2, b3)  # b1 or b2 or b3 (at least one)
model.AddBoolAnd(b1, b2.Not(), b3.Not())  # b1 and not b2 and not b3 (all)
model.AddBoolXOr(b1, b2, b3)  # b1 xor b2 xor b3
model.AddImplication(b1, b2)  # b1 -> b2
```

In this context you could also mention `AddAtLeastOne`, `AddAtMostOne`, and `AddExactlyOne`, but these can also be
modelled as linear constraints.

### Conditional Constraints

Linear constraints (Add), BoolOr, and BoolAnd support being activated by a condition.
This is not only a very helpful constraint for many applications, but it is also a constraint that is highly inefficient
to model with linear optimization ([Big M Method](https://en.wikipedia.org/wiki/Big_M_method)).
My current experience shows that CP-SAT can work much more efficiently with this kind of constraint.
Note that you only can use a boolean variable and not directly add an expression, i.e., maybe you need to create an
auxiliary variable.

```python
model.Add(x + z == 2 * y).OnlyEnforceIf(b1)
model.Add(x + z == 10).OnlyEnforceIf([b2, b3.Not()])  # only enforce if b2 AND NOT b3
```

### AllDifferent

A constraint that is often seen in Constraint Programming, but I myself was always able to deal without it.
Still, you may find it important. It forces all (integer) variables to have a different value.

`AllDifferent` is actually the only constraint that may use a domain based propagator (if it is not a
permutation) [[source](https://youtu.be/lmy1ddn4cyw?t=624)]

```python
model.AddAllDifferent(x, y, z)

# You can also add a constant to the variables.
vars = [model.NewIntVar(0, 10) for i in range(10)]
model.AddAllDifferent(x+i for i, x in enumerate(vars))
```

The [N-queens](https://developers.google.com/optimization/cp/queens) example of the official tutorial makes use of this constraint.

There is a big caveat with this constraint:
CP-SAT now has a preprocessing step that automatically tries to infer large `AllDifferent` constraints from sets of mutual `!=` constraints.
This inference equals the NP-hard Edge Clique Cover problem, thus, is not a trivial task.
If you add an `AllDifferent` constraint yourself, CP-SAT will assume that you already took care of this inference and will skip this step.
Thus, adding a single `AllDifferent` constraint can make your model significantly slower, if you also use `!=` constraints.
If you do not use `!=` constraints, you can safely use `AllDifferent` without any performance penalty.
You may also want to use `!=` instead of `AllDifferent` if you apply it to overlapping sets of variables without proper optimization, because then CP-SAT will do the inference for you.

In [./examples/add_all_different.ipynb](./examples/add_all_different.ipynb) you can find a quick experiment based on the graph coloring problem.
In the graph coloring problem, the colors of two adjacent vertices have to be different.
This can be easily modelled by `!=` or `AllDifferent` constraints on every edge.
Using `!=`, we can solve the example graph in around 5 seconds.
If we use `AllDifferent`, it takes more than 5 minutes.
If we manually disable the `AllDifferent` inference, it also takes more than 5 minutes.
Same if we add just a single `AllDifferent` constraint.
Thus, if you use `AllDifferent` do it properly on large sets, or use `!=` constraints and let CP-SAT infer the `AllDifferent` constraints for you.

Maybe CP-SAT will allow you to use `AllDifferent` without any performance penalty in the future, but for now, you have to be aware of this. See also [the optimization parameter documentation](https://github.com/google/or-tools/blob/1d696f9108a0ebfd99feb73b9211e2f5a6b0812b/ortools/sat/sat_parameters.proto#L542).


### Absolute Values and Max/Min

Two often occurring and important operators are absolute values as well as minimum and maximum values.
You cannot use operators directly in the constraints, but you can use them via an auxiliary variable and a dedicated
constraint.
These constraints are reasonably efficient in my experience.

```python
# abs_xz == |x+z|
abs_xz = model.NewIntVar(0, 200, "|x+z|")  # ub = ub(x)+ub(z)
model.AddAbsEquality(target=abs_xz, expr=x + z)
# max_xyz = max(x,y,z)
max_xyz = model.NewIntVar(0, 100, "max(x,y, z)")
model.AddMaxEquality(max_xyz, [x, y, z])
# min_xyz = min(x,y,z)
min_xyz = model.NewIntVar(-100, 100, " min(x,y, z)")
model.AddMinEquality(min_xyz, [x, y, z])
```

### Multiplication and Modulo

A big nono in linear optimization (the most successful optimization area) are multiplication of variables (because this
would no longer be linear, right...).
Often we can linearize the model by some tricks and tools like Gurobi are also able to do some non-linear optimization (
in the end, it is most often translated to a less efficient linear model again).
CP-SAT can also work with multiplication and modulo of variables, again as constraint not as operation.
So far, I have not made good experience with these constraints, i.e., the models end up being slow to solve,
and would recommend to only use them if you really need them and cannot find a way around them.

```python
xyz = model.NewIntVar(-100 * 100 * 100, 100 ** 3, 'x*y*z')
model.AddMultiplicationEquality(xyz, [x, y, z])  # xyz = x*y*z
model.AddModuloEquality(x, y, 3)  # x = y % 3
```

> :warning: The documentation indicates that multiplication of more than two variables is supported, but I got
> an error when trying it out. I have not investigated this further, as I would expect it to be slow anyway.


### Circuit/Tour-Constraints

The [Traveling Salesman Problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem) or Hamiltonicity
Problem are important and difficult problems that occur as subproblem in many contexts.
For solving the classical TSP, you should use the extremely powerful
solver [Concorde](https://www.math.uwaterloo.ca/tsp/concorde.html). There is also a
separate [part in ortools](https://developers.google.com/optimization/routing) dedicated to routing.
If it is just a subproblem, you can add a simple constraint by encoding the allowed edges as triples of start vertex
index, target vertex index, and literal/variable.
Note that this is using directed edges/arcs.
By adding a triple (v,v,var), you can allow CP-SAT to skip the vertex v.

> If the tour-problem is the fundamental part of your problem, you may be better served with using a Mixed Integer
Programming solver. Don't expect to solve tours much larger than 250 vertices with CP-SAT.

```python
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
     (2, 3): 27
 }
 model = cp_model.CpModel()
 # Variables: Binary decision variables for the edges
 edge_vars = { 
     (u,v): model.NewBoolVar(f"e_{u}_{v}") for (u,v) in dgraph.keys()
 }
 # Constraints: Add Circuit constraint
 # We need to tell CP-SAT which variable corresponds to which edge.
 # This is done by passing a list of tuples (u,v,var) to AddCircuit.
 circuit = [(u, v, var)  # (source, destination, variable)
             for (u,v), var in edge_vars.items()]
 model.AddCircuit(circuit)

 # Objective: minimize the total cost of edges
 obj = sum(dgraph[(u,v)]*x for (u,v),x  in edge_vars.items())
 model.Minimize(obj)

 # Solve
 solver = cp_model.CpSolver()
 status = solver.Solve(model)
 assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
 tour = [(u,v) for (u,v),x in edge_vars.items() if solver.Value(x)]
 print("Tour:", tour)
```
    Tour: [(0, 1), (2, 0), (3, 2), (1, 3)]

You can use this constraint very flexibly for many tour problems.
We added three examples:
* [./examples/add_circuit.py](./examples/add_circuit.py): The example above, slightly extended. Find out how large you can make the graph.
* [./examples/add_circuit_budget.py](./examples/add_circuit_budget.py): Find the largest tour with a given budget. This will be a bit more difficult to solve.
* [./examples/add_circuit_multi_tour.py](./examples/add_circuit_multi_tour.py): Allow $k$ tours, which in sum need to be minimal and cover all vertices.

The most powerful TSP-solver *concorde* uses a linear programming based approach, but with a lot of additional
techniques to improve the performance. The book *In Pursuit of the Traveling Salesman* by William Cook may have already given
you some insights. For more details, you can also read the more advanced book *The Traveling Salesman Problem: A Computational Study* by Applegate, Bixby, Chvatál, and Cook.
If you need to solve some variant, MIP-solvers (which could be called a generalization of that approach) are known to perform
well using the [Dantzig-Fulkerson-Johnson Formulation](https://en.wikipedia.org/wiki/Travelling_salesman_problem#Dantzig%E2%80%93Fulkerson%E2%80%93Johnson_formulation).
This model is theoretically exponential, but using lazy constraints (which are added when needed), it can be solved
efficiently in practice. The [Miller-Tucker-Zemlin formulation](https://en.wikipedia.org/wiki/Travelling_salesman_problem#Miller%E2%80%93Tucker%E2%80%93Zemlin_formulation[21])
allows a small formulation size, but is bad in practice with MIP-solvers due to its weak linear relaxations.
Because CP-SAT does not allow lazy constraints, the Danzig-Fulkerson-Johnson formulation would require many iterations and a lot of wasted resources.
As CP-SAT does not suffer as much from weak linear relaxations (replacing Big-M by logic constraints, such as `OnlyEnforceIf`), the Miller-Tucker-Zemlin formulation may be an option in some cases, though a simple experiment (see below) shows a similar performance as the iterative approach.
When using `AddCircuit`, CP-SAT will actually use the LP-technique for the linear relaxation (so using this constraint may really help, as
otherwise CP-SAT will not know that your manual constraints are actually a tour with a nice linear relaxation), and probably has the lazy constraints implemented internally.
Using the `AddCircuit` constraint is thus highly recommendable for any circle or path constraints.

In [./examples/add_circuit_comparison.ipynb](./examples/add_circuit_comparison.ipynb), we compare the performance of some models for the TSP, to
estimate the performance of CP-SAT for the TSP.

* **AddCircuit** can solve the Euclidean TSP up to a size of around 110 vertices in 10 seconds to optimality.
* **MTZ (Miller-Tucker-Zemlin)** can solve the eculidean TSP up to a size of around 50 vertices in 10 seconds to optimality.
* **Dantzig-Fulkerson-Johnson via iterative solving** can solve the eculidean TSP up to a size of around 50 vertices in 10 seconds to optimality.
* **Dantzig-Fulkerson-Johnson via lazy constraints in Gurobi** can solve the eculidean TSP up to a size of around 225 vertices in 10 seconds to optimality.

This tells you to use a MIP-solver for problems dominated by the tour constraint, and if you have to use CP-SAT, you should definitely use the `AddCircuit` constraint.

> These are all naive implementations, and the benchmark is not very rigorous. These values are only meant to give you
> a rough idea of the performance. Additionally, this benchmark was regarding proving *optimality*. The performance in
> just optimizing a tour could be different. The numbers could also look different for differently generated instances.

> :warning: This section could need some more work, as it is relatively important. I just did some experiments, and hastily jotted down some notes here.

### Array operations

You can even go completely bonkers and work with arrays in your model.
The element at a variable index can be accessed via an `AddElement` constraint.

The second constraint is actually more of a stable matching in array form.
For two arrays of variables $v,w, |v|=|w|$, it requires 
$v[i]=j \Leftrightarrow w[j]=i \quad \forall i,j \in 0,\ldots,|v|-1$.
Note that this restricts the values of the variables in the arrays to $0,\ldots, |v|-1$.

```python
# ai = [x,y,z][i]  assign ai the value of the i-th entry.
ai = model.NewIntVar(-100, 100, "a[i]")
i = model.NewIntVar(0, 2, "i")
model.AddElement(index=i, variables=[x, y, z], target=ai)

model.AddInverse([x, y, z], [z, y, x])
```

### Interval Variables and No-Overlap Constraints

CP-SAT also supports interval variables and corresponding constraints.
These are important for scheduling and packing problems.
There are simple no-overlap constraints for intervals for one-dimensional and two-dimensional intervals.
In two-dimensional intervals, only one dimension is allowed to overlap, i.e., the other dimension has to be disjoint.
This is essentially rectangle packing.
Let us see how we can model a simple 2-dimensional packing problem.
Note that `NewIntervalVariable` may indicate a new variable, but it is actually a constraint container in which you have to insert the classical integer variables.
This constraint container is required, e.g., for the no-overlap constraint.

```python
from ortools.sat.python import cp_model

# Instance
container = (40, 15)
boxes = [
    (11, 3),
    (13, 3),
    (9,  2),
    (7,  2),
    (9,  3),
    (7,  3),
    (11, 2),
    (13, 2),
    (11, 4),
    (13, 4),
    (3,  5),
    (11, 2),
    (2,  2),
    (11, 3),
    (2,  3),
    (5,  4),
    (6,  4),
    (12, 2),
    (1,  2),
    (3,  5),
    (13, 5),
    (12, 4),
    (1,  4),
    (5,  2),
    #(6,  2),  # add to make tight
    # (6,3), # add to make infeasible
]
model = cp_model.CpModel()

# We have to create the variable for the bottom left corner of the boxes.
# We directly limit their range, such that the boxes are inside the container
x_vars = [model.NewIntVar(0, container[0]-box[0], name = f'x1_{i}') for i, box in enumerate(boxes)]
y_vars = [model.NewIntVar(0, container[1]-box[1], name = f'y1_{i}') for i, box in enumerate(boxes)]
# Interval variables are actually more like constraint containers, that are then passed to the no overlap constraint
# Note that we could also make size and end variables, but we don't need them here
x_interval_vars = [model.NewIntervalVar(start=x_vars[i], size=box[0], end=x_vars[i]+box[0], name = f'x_interval_{i}') for i, box in enumerate(boxes)]
y_interval_vars = [model.NewIntervalVar(start=y_vars[i], size=box[1], end=y_vars[i]+box[1], name = f'y_interval_{i}') for i, box in enumerate(boxes)]
# Enforce that no two rectangles overlap
model.AddNoOverlap2D(x_interval_vars, y_interval_vars)

# Solve!
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
solver.log_callback = print
status = solver.Solve(model)
assert status == cp_model.OPTIMAL
for i, box in enumerate(boxes):
    print(f'box {i} is placed at ({solver.Value(x_vars[i])}, {solver.Value(y_vars[i])})')

```

> The keywords `start` may be named `begin` in some versions of ortools.

See [this notebook](./examples/add_no_overlap_2d.ipynb) for the full example.

There is also the option for optional intervals, i.e., intervals that may be skipped.
This would allow you to have multiple containers or do a knapsack-like packing.

The resolution seems to be quite important for this problem, as mentioned before.
The following table shows the runtime for different resolutions (the solution is always the same, just scaled).

| Resolution | Runtime |
|------------|---------|
| 1x         | 0.02s   |
| 10x        | 0.7s    |
| 100x       | 7.6s    |
| 1000x      | 75s     |
| 10_000x    | >15min  |

See [this notebook](./examples/add_no_overlap_2d_scaling.ipynb) for the full example.

### There is more

CP-SAT has even more constraints, but I think I covered the most important ones.
If you need more, you can check out the [official documentation](https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel).


---

## Parameters

The CP-SAT solver has a lot of parameters to control its behavior.
They are implemented via [Protocol Buffer](https://developers.google.com/protocol-buffers) and can be manipulated via
the `parameters`-member.
If you want to find out all options, you can check the reasonably well documented `proto`-file in
the [official repository](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto).
I will give you the most important right below.

> :warning: Only a few of the parameters (e.g., timelimit) are beginner-friendly. Most other parameters (e.g., decision strategies)
> should not be touched as the defaults are well-chosen, and it is likely that you will interfere with some optimizations.
> If you need a better performance, try to improve your model of the optimization problem.

### Time limit and Status

If we have a huge model, CP-SAT may not be able to solve it to optimality (if the constraints are not too difficult,
there is a good chance we still get a good solution).
Of course, we don't want CP-SAT to run endlessly for hours (years, decades,...) but simply abort after a fixed time and
return us the best solution so far.
If you are now asking yourself why you should use a tool that may run forever: There are simply no provably faster
algorithms and considering the combinatorial complexity, it is incredible that it works so well.
Those not familiar with the concepts of NP-hardness and combinatorial complexity, I recommend reading the book 'In
Pursuit of the Traveling Salesman' by William Cook.
Actually, I recommend this book to anyone into optimization: It is a beautiful and light weekend-read.

To set a time limit (in seconds), we can simply set the following value before we run the solver:

```python
solver.parameters.max_time_in_seconds = 60  # 60s timelimit
```

We now of course have the problem, that maybe we won't have an optimal solution, or a solution at all, we can continue
on.
Thus, we need to check the status of the solver.

```python
status = solver.Solve(model)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("We have a solution.")
else:
    print("Help?! No solution available! :( ")
```

The following status codes are possible:

* `OPTIMAL`: Perfect, we have an optimal solution.
* `FEASIBLE`: Good, we have at least a feasible solution (we may also have a bound available to check the quality
  via `solver.BestObjectiveBound()`).
* `INFEASIBLE`: There is a proof that no solution can satisfy all our constraints.
* `MODEL_INVALID`: You used CP-SAT wrongly.
* `UNKNOWN`: No solution was found, but also no infeasibility proof. Thus, we actually know nothing. Maybe there is at
  least a bound available?

If you want to print the status, you can use `solver.StatusName(status)`.

We can not only limit the runtime but also tell CP-SAT, we are satisfied with a solution within a specific, provable
quality range.
For this, we can set the parameters `absolute_gap_limit` and `relative_gap_limit`.
The absolute limit tells CP-SAT to stop as soon as the solution is at most a specific value apart to the bound, the
relative limit is relative to the bound.
More specifically, CP-SAT will stop as soon as the objective value(O) is within relative ratio
$abs(O - B) / max(1, abs(O))$ of the bound (B).
To stop as soon as we are within 5% of the optimum, we could state (TODO: Check)

```python
solver.parameters.relative_gap_limit = 0.05
```

Now we may want to stop after we didn't make progress for some time or whatever.
In this case, we can make use of the solution callbacks.

> For those familiar with Gurobi: Unfortunately, we can only abort the solution progress and not add lazy constraints or
> similar.
> For those not familiar with Gurobi or MIPs: With Mixed Integer Programming we can adapt the model during the solution
> process via callbacks which allows us to solve problems with many(!) constraints by only adding them lazily. This is currently
> the biggest shortcoming of CP-SAT for me. Sometimes you can still do dynamic model building with only little overhead 
> feeding information of previous iterations into the model

For adding a solution callback, we have to inherit from a base class.
The documentation of the base class and the available operations can be found in
the [documentation](https://google.github.io/or-tools/python/ortools/sat/python/cp_model.html#CpSolverSolutionCallback).

```python
class MySolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, stuff):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.stuff = stuff  # just to show that we can save some data in the callback.

    def on_solution_callback(self):
        obj = self.ObjectiveValue()  # best solution value
        bound = self.BestObjectiveBound()  # best bound
        print(f"The current value of x is {self.Value(x)}")
        if abs(obj - bound) < 10:
            self.StopSearch()  # abort search for better solution
        # ...


solver.Solve(model, MySolutionCallback(None))
```

You can find
an [official example of using such callbacks](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/stop_after_n_solutions_sample_sat.py)
.

Beside querying the objective value of the currently best solution, the solution itself, and the best known bound, you
can also find out about internals such as `NumBooleans(self)`, `NumConflicts(self)`, `NumBranches(self)`. What those
values mean will be discussed later.

### Parallelization

CP-SAT has some basic parallelization. It can be considered a portfolio-strategy with some minimal data exchange between
the threads. The basic idea is to use different techniques and may the best fitting one win (as an experienced
optimizer, it can actually be very enlightening to see which technique contributed how much at which phase as visible in the logs).

1. The first thread performs the default search: The optimization problem is converted into a Boolean satisfiability
   problem and solved with a Variable State Independent Decaying Sum (VSIDS) algorithm. A search heuristic introduces
   additional literals for branching when needed, by selecting an integer variable, a value and a branching direction.
   The model also gets linearized to some degree, and the corresponding LP gets (partially) solved with the (dual)
   Simplex-algorithm to support the satisfiability model.
2. The second thread uses a fixed search if a decision strategy has been specified. Otherwise, it tries to follow the
   LP-branching on the linearized model.
3. The third thread uses Pseudo-Cost branching. This is a technique from mixed integer programming, where we branch on
   the variable that had the highest influence on the objective in prior branches. Of course, this only provides useful
   values after we have already performed some branches on the variable.
4. The fourth thread is like the first thread but without linear relaxation.
5. The fifth thread does the opposite and uses the default search but with maximal linear relaxation, i.e., also
   constraints that are more expensive to linearize are linearized. This can be computationally expensive but provides
   good lower bounds for some models.
6. The sixth thread performs a core based search from the SAT- community. This approach extracts unsatisfiable cores of
   the formula and is good for finding lower bounds.
7. All further threads perform a Large Neighborhood Search (LNS) for obtaining good solutions.

Note that this information may no longer be completely accurate (if it ever was).
To set the number of used cores/workers, simply do:

```python
solver.parameters.num_search_workers = 8  # use 8 cores
```

If you want to use more LNS-worker, you can specify `solver.parameters.min_num_lns_workers` (default 2).
You can also specify how the different cores should be used by configuring/reordering.

```
solver.parameters.subsolvers = ["default_lp", "fixed", "less_encoding", "no_lp", "max_lp", "pseudo_costs", "reduced_costs", "quick_restart", "quick_restart_no_lp", "lb_tree_search", "probing"]
 ```

This can be interesting, e.g., if you are using CP-SAT especially because the linear
relaxation is not useful (and the BnB-algorithm performing badly). There are
even more options, but for these you can simply look into the
[documentation](https://github.com/google/or-tools/blob/49b6301e1e1e231d654d79b6032e79809868a70e/ortools/sat/sat_parameters.proto#L513).
Be aware that fine-tuning such a solver is not a simple task, and often you do more harm than good by tinkering around.
However, I noticed that decreasing the number of search workers can actually improve the runtime for some problems.
This indicates that at least selecting the right subsolvers that are best fitted for your problem can be worth a shot.
For example `max_lp` is probably a waste of resources if you know that your model has a terrible linear relaxation.
In this context I want to recommend having a look on some relaxed solutions when dealing with difficult problems to get a
better understanding of which parts a solver may struggle with (use a linear programming solver, like Gurobi, for this).

### Assumptions

Quite often you want to find out what happens if you force some variables to a specific value.
Because you possibly want to do that multiple times, you do not want to copy the whole model.
CP-SAT has a nice option of adding assumptions that you can clear afterwards, without needing to copy the object to test
the next assumptions.
This is a feature also known from many SAT-solvers and CP-SAT also only allows this feature for boolean literals.
You cannot add any more complicated expressions here, but for boolean literals it seems to be pretty efficient.
By adding some auxiliary boolean variables, you can also use this technique to play around with more complicated
expressions without the need to copy the model.
If you really need to temporarily add complex constraints, you may have to copy the model using `model.CopyFrom` (maybe
you also need to copy the variables. Need to check that.).

```python
model.AddAssumptions([b1, b2.Not()])  # assume b1=True, b2=False
model.AddAssumption(b3)  # assume b3=True (single literal)
# ... solve again and analyse ...
model.ClearAssumptions()  # clear all assumptions
```

> An **assumption** is a temporary fixation of a boolean variable to true or false. It can be efficiently handled by a
> SAT-solver (and thus probably also by CP-SAT) and does not harm the learned clauses (but can reuse them).

### Hints

Maybe we already have a good intuition on how the solution will look like (this could be, because we already solved a
similar model, have a good heuristic, etc.).
In this case it may be useful, to tell CP-SAT about it, so it can incorporate this knowledge into its search.
For Mixed Integer Programming Solver, this often yields a visible boost, even with mediocre heuristic solutions.
For CP-SAT I actually also encountered downgrades of the performance if the hints weren't great (but this may
depend on the problem).

```python
model.AddHint(x, 1)  # Tell CP-SAT that x will probably be 1
model.AddHint(y, 2)  # and y probably be 2.
```

You can also
find [an official example](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/solution_hinting_sample_sat.py).

To make sure, your hints are actually correct, you can use the following parameters to make CP-SAT throw an error if
your hints are wrong.

```python
solver.parameters.debug_crash_on_bad_hint = True
```

If you have the feeling that your hints are not used, you may have made a logical error in your model or just have
a bug in your code.
This parameter will tell you about it.

(TODO: Have not tested this, yet)

### Logging

Sometimes it is useful to activate logging to see what is going on.
This can be achieved by setting the following two parameters.

```python
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
solver.log_callback = print  # (str)->None
```
If you get a doubled output, remove the last line.

The output can look as follows:
```
Starting CP-SAT solver v9.3.10497
Parameters: log_search_progress: true
Setting number of workers to 16

Initial optimization model '':
#Variables: 290 (#ints:1 in objective)
  - 290 in [0,17]
#kAllDiff: 34
#kLinMax: 1
#kLinear2: 2312 (#complex_domain: 2312)

Starting presolve at 0.00s
[ExtractEncodingFromLinear] #potential_supersets=0 #potential_subsets=0 #at_most_one_encodings=0 #exactly_one_encodings=0 #unique_terms=0 #multiple_terms=0 #literals=0 time=9.558e-06s
[Probing] deterministic_time: 0.053825 (limit: 1) wall_time: 0.0947566 (12427/12427)
[Probing]  - new integer bounds: 1
[Probing]  - new binary clause: 9282
[DetectDuplicateConstraints] #duplicates=0 time=0.00993671s
[DetectDominatedLinearConstraints] #relevant_constraints=2312 #work_done=14118 #num_inclusions=0 #num_redundant=0 time=0.0013379s
[DetectOverlappingColumns] #processed_columns=0 #work_done=0 #nz_reduction=0 time=0.00176239s
[ProcessSetPPC] #relevant_constraints=612 #num_inclusions=0 work=29376 time=0.0022503s
[Probing] deterministic_time: 0.0444515 (limit: 1) wall_time: 0.0820382 (11849/11849)
[Probing]  - new binary clause: 9282
[DetectDuplicateConstraints] #duplicates=0 time=0.00786558s
[DetectDominatedLinearConstraints] #relevant_constraints=2312 #work_done=14118 #num_inclusions=0 #num_redundant=0 time=0.000688681s
[DetectOverlappingColumns] #processed_columns=0 #work_done=0 #nz_reduction=0 time=0.000992311s
[ProcessSetPPC] #relevant_constraints=612 #num_inclusions=0 work=29376 time=0.00121334s

Presolve summary:
  - 0 affine relations were detected.
  - rule 'all_diff: expanded' was applied 34 times.
  - rule 'deductions: 10404 stored' was applied 1 time.
  - rule 'linear: simplified rhs' was applied 7514 times.
  - rule 'presolve: 0 unused variables removed.' was applied 1 time.
  - rule 'presolve: iteration' was applied 2 times.
  - rule 'variables: add encoding constraint' was applied 5202 times.

Presolved optimization model '':
#Variables: 5492 (#ints:1 in objective)
  - 5202 in [0,1]
  - 289 in [0,17]
  - 1 in [1,17]
#kAtMostOne: 612 (#literals: 9792)
#kLinMax: 1
#kLinear1: 10404 (#enforced: 10404)
#kLinear2: 2312 (#complex_domain: 2312)

Preloading model.
#Bound   0.45s best:inf   next:[1,17]     initial_domain

Starting Search at 0.47s with 16 workers.
9 full subsolvers: [default_lp, no_lp, max_lp, reduced_costs, pseudo_costs, quick_restart, quick_restart_no_lp, lb_tree_search, probing]
Interleaved subsolvers: [feasibility_pump, rnd_var_lns_default, rnd_cst_lns_default, graph_var_lns_default, graph_cst_lns_default, rins_lns_default, rens_lns_default]
#1       0.71s best:17    next:[1,16]     quick_restart_no_lp fixed_bools:0/11849
#2       0.72s best:16    next:[1,15]     quick_restart_no_lp fixed_bools:289/11849
#3       0.74s best:15    next:[1,14]     no_lp fixed_bools:867/11849
#Bound   1.30s best:15    next:[8,14]     max_lp initial_propagation
#Done    3.40s max_lp
#Done    3.40s probing

Sub-solver search statistics:
  'max_lp':
     LP statistics:
       final dimension: 2498 rows, 5781 columns, 106908 entries with magnitude in [6.155988e-02, 1.000000e+00]
       total number of simplex iterations: 3401
       num solves: 
         - #OPTIMAL: 6
         - #DUAL_UNBOUNDED: 1
         - #DUAL_FEASIBLE: 1
       managed constraints: 5882
       merged constraints: 3510
       coefficient strenghtenings: 19
       num simplifications: 1
       total cuts added: 3534 (out of 4444 calls)
         - 'CG': 1134
         - 'IB': 150
         - 'MIR_1': 558
         - 'MIR_2': 647
         - 'MIR_3': 490
         - 'MIR_4': 37
         - 'MIR_5': 60
         - 'MIR_6': 20
         - 'ZERO_HALF': 438

  'reduced_costs':
     LP statistics:
       final dimension: 979 rows, 5781 columns, 6456 entries with magnitude in [3.333333e-01, 1.000000e+00]
       total number of simplex iterations: 1369
       num solves: 
         - #OPTIMAL: 15
         - #DUAL_FEASIBLE: 51
       managed constraints: 2962
       merged constraints: 2819
       shortened constraints: 1693
       coefficient strenghtenings: 675
       num simplifications: 1698
       total cuts added: 614 (out of 833 calls)
         - 'CG': 7
         - 'IB': 439
         - 'LinMax': 1
         - 'MIR_1': 87
         - 'MIR_2': 80

  'pseudo_costs':
     LP statistics:
       final dimension: 929 rows, 5781 columns, 6580 entries with magnitude in [3.333333e-01, 1.000000e+00]
       total number of simplex iterations: 1174
       num solves: 
         - #OPTIMAL: 14
         - #DUAL_FEASIBLE: 33
       managed constraints: 2923
       merged constraints: 2810
       shortened constraints: 1695
       coefficient strenghtenings: 675
       num simplifications: 1698
       total cuts added: 575 (out of 785 calls)
         - 'CG': 5
         - 'IB': 400
         - 'LinMax': 1
         - 'MIR_1': 87
         - 'MIR_2': 82

  'lb_tree_search':
     LP statistics:
       final dimension: 929 rows, 5781 columns, 6650 entries with magnitude in [3.333333e-01, 1.000000e+00]
       total number of simplex iterations: 1249
       num solves: 
         - #OPTIMAL: 16
         - #DUAL_FEASIBLE: 14
       managed constraints: 2924
       merged constraints: 2809
       shortened constraints: 1692
       coefficient strenghtenings: 675
       num simplifications: 1698
       total cuts added: 576 (out of 785 calls)
         - 'CG': 8
         - 'IB': 400
         - 'LinMax': 2
         - 'MIR_1': 87
         - 'MIR_2': 79


Solutions found per subsolver:
  'no_lp': 1
  'quick_restart_no_lp': 2

Objective bounds found per subsolver:
  'initial_domain': 1
  'max_lp': 1

Improving variable bounds shared per subsolver:
  'no_lp': 579
  'quick_restart_no_lp': 1159

CpSolverResponse summary:
status: OPTIMAL
objective: 15
best_bound: 15
booleans: 12138
conflicts: 0
branches: 23947
propagations: 408058
integer_propagations: 317340
restarts: 23698
lp_iterations: 1174
walltime: 3.5908
usertime: 3.5908
deterministic_time: 6.71917
gap_integral: 11.2892
```

The log is actually very interesting to understand CP-SAT, but also to learn about the optimization problem at hand.
It gives you a lot of details on, e.g., how many variables could be directly removed or which techniques contributed to lower and upper bounds the most.
We take a more detailed look onto the log [here](./understanding_the_log.md).

### Decision Strategy

In the end of this section, a more advanced parameter that looks interesting for advanced users as it gives some insights into the search algorithm, **but is probably better left alone**.

We can tell CP-SAT, how to branch (or make a decision) whenever it can no longer deduce anything via propagation.
For this, we need to provide a list of the variables (order may be important for some strategies), define which variable
should be selected next (fixed variables are automatically skipped), and define which value should be probed.

We have the following options for variable selection:

* `CHOOSE_FIRST`: the first not-fixed variable in the list.
* `CHOOSE_LOWEST_MIN`: the variable that could (potentially) take the lowest value.
* `CHOOSE_HIGHEST_MAX`: the variable that could (potentially) take the highest value.
* `CHOOSE_MIN_DOMAIN_SIZE`: the variable that has the fewest feasible assignments.
* `CHOOSE_MAX_DOMAIN_SIZE`: the variable the has the most feasible assignments.

For the value/domain strategy, we have the options:

* `SELECT_MIN_VALUE`: try to assign the smallest value.
* `SELECT_MAX_VALUE`: try to assign the largest value.
* `SELECT_LOWER_HALF`: branch to the lower half.
* `SELECT_UPPER_HALF`: branch to the upper half.
* `SELECT_MEDIAN_VALUE`: try to assign the median value.

> **CAVEAT:** In the documentation there is a warning about the completeness of the domain strategy. I am not sure, if
> this is just for custom strategies or you have to be careful in general. So be warned.

```python
model.AddDecisionStrategy([x], cp_model.CHOOSE_FIRST, cp_model.SELECT_MIN_VALUE)

# your can force CP-SAT to follow this strategy exactly
solver.parameters.search_branching = cp_model.FIXED_SEARCH
```

For example for [coloring](https://en.wikipedia.org/wiki/Graph_coloring) (with integer representation of the color), we could order the
variables by decreasing neighborhood size (`CHOOSE_FIRST`) and then always try to assign
the lowest color (`SELECT_MIN_VALUE`). This strategy should perform an implicit
kernelization, because if we need at least $k$ colors, the vertices with less than $k$
neighbors are trivial (and they would not be relevant for any conflict).
Thus, by putting them at the end of the list, CP-SAT will only consider them once
the vertices with higher degree could be colored without any conflict (and then the
vertices with lower degree will, too).
Another strategy may be to use `CHOOSE_LOWEST_MIN` to always
select the vertex that has the lowest color available.
Whether this will actually help, has to be evaluated: CP-SAT will probably notice
by itself which vertices are the critical ones after some conflicts.

> :warning: I played around a little with selecting a manual search strategy. But even for the coloring, where this may even
> seem smart, it only gave an advantage for a bad model and after improving the model by symmetry breaking, it performed worse.
> Further, I assume that CP-SAT can learn the best strategy (Gurobi does such a thing, too) much better dynamically on its own.

---

## How does it work?

CP-SAT is a versatile *portfolio* solver, centered around a *Lazy Clause Generation (LCG)* based Constraint Programming Solver, although it encompasses a broader spectrum of technologies.

In its role as a portfolio solver, CP-SAT concurrently executes a multitude of diverse algorithms and strategies, each possessing unique strengths and weaknesses.
These elements operate largely independently but engage in information exchange, sharing progress when better solutions emerge or tighter bounds become available.

While this may initially appear as an inefficient approach due to potential redundancy, it proves highly effective in practice.
The rationale behind this lies in the inherent challenge of predicting which algorithm is best suited to solve a given problem (No Free Lunch Theorem).
Thus, the pragmatic strategy involves running various approaches in parallel, with the hope that one will effectively address the problem at hand.
Note that you can also specify which algorithms should be used if you already know which strategies are promising or futile.

In contrast, Branch and Cut-based Mixed Integer Programming solvers like Gurobi implement a more efficient partitioning of the search space to reduce redundancy.
However, they specialize in a particular strategy, which may not always be the optimal choice, although it frequently proves to be so.

CP-SAT employs Branch and Cut techniques, including linear relaxations and cutting planes, as part of its toolkit.
Models that can be efficiently addressed by a Mixed Integer Programming (MIP) solver are typically a good match for CP-SAT as well.
Nevertheless, CP-SAT's central focus is the implementation of Lazy Clause Generation, harnessing SAT-solvers rather than relying primarily on linear relaxations.
As a result, CP-SAT may exhibit somewhat reduced performance when confronted with MIP problems compared to dedicated MIP solvers.
However, it gains a distinct advantage when dealing with problems laden with intricate logical constraints.

The concept behind Lazy Clause Generation involves the (incremental) transformation of the problem into a SAT-formula, subsequently employing a SAT-solver to seek a solution (or prove bounds by infeasibility).
To mitigate the impracticality of a straightforward conversion, Lazy Clause Generation leverages an abundance of lazy variables and clauses.

Notably, the [Cook-Levin Theorem](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem) attests that any problem within the realm of NP can be translated into a SAT-formula.
Optimization, in theory, could be achieved through a simple binary search.
However, this approach, while theoretically sound, lacks efficiency.
CP-SAT employs a more refined encoding scheme to tackle optimization problems more effectively.

If you want to understand the inner workings of CP-SAT, you can follow the following learning path:

1. Learn how to get a feasible solution based on boolean logics with SAT-solvers: Backtracking, DPLL, CDCL, VSIDS, ...
    * [Historical Overview by Armin Biere](https://youtu.be/DU44Y9Pt504) (video)
    * [Donald Knuth - The Art of Computer Programming, Volume 4, Fascicle 6: Satisfiability](https://www-cs-faculty.stanford.edu/~knuth/taocp.html) (book)
    * [Carsten Sinz and Tomas Baylo - Practical SAT Solving](https://baldur.iti.kit.edu/sat/#about) (slides)
2. Learn how to get provably optimal solutions via classical Mixed Integer Programming:
    * Linear Programming: Simplex, Duality, Dual Simplex, ...
        * [Understanding and Using Linear Programming](https://link.springer.com/book/10.1007/978-3-540-30717-4) (book)
    * Mixed Integer Programming: Branch and Bound, Cutting Planes, Branch and Cut, ...
        * [Discrete Optimization on Coursera](https://www.coursera.org/learn/discrete-optimization) (video course)
        * [Gurobi Resources](https://www.gurobi.com/resource/mip-basics/) (website)
3. Learn the additional concepts of LCG Constraint Programming: Propagation, Lazy Clause Generation, ...
    * [Combinatorial Optimisation and Constraint Programming by Prof. Pierre Flener at Uppsala University in Sweden](https://user.it.uu.se/~pierref/courses/COCP/slides/) (slides)
    * [Talk by Peter Stucky](https://www.youtube.com/watch?v=lxiCHRFNgno) (video)
4. Learn the details of CP-SAT:
    * [The proto-file of the parameters](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto) (source)
    * [The complete source code](https://github.com/google/or-tools/tree/stable/ortools/sat) (source)
    * [A talk by the developers of CP-SAT](https://youtu.be/lmy1ddn4cyw) (video)

If you already have a background in Mixed Integer Programming, you may directly jump into the slides of [Combinatorial Optimisation and Constraint Programming](https://user.it.uu.se/~pierref/courses/COCP/slides/).
This is a full and detailed course on constraint programming, and will probably take you some time to work through.
However, it gives you all the knowledge you need to understand the constraint programming part of CP-SAT.

> Originally, I wrote a short introduction into each of the topics, but I decided to remove them as the material I linked to is much better than what I could have written.
> You can find a backup of the old version [here](./old_how_does_it_work.md).

### What happens in CP-SAT on solve?

What actually happens when you execute `solver.Solve(model)`?

1. The model is read.
2. The model is verified.
3. Preprocessing (multiple iterations):
    1. Presolve (domain reduction)
    2. Expanding higher-level constraints to lower-level constraints. See also the analogous [FlatZinc and Flattening](https://www.minizinc.org/doc-2.5.5/en/flattening.html).
    3. Detection of equivalent variables and [affine relations](https://personal.math.ubc.ca/~cass/courses/m309-03a/a1/olafson/affine_fuctions.htm).
    4. Substitute these by canonical representations
    5. Probe some variables to detect if they are actually fixed or detect further equivalences.
4. Load the preprocessed model into the underlying solver and create the linear relaxations.
5. **Search for solutions and bounds with the different solvers until the lower and upper bound match or another termination criterion is reached (e.g., time limit)**
6. Transform solution back to original model.

This is taken from [this talk](https://youtu.be/lmy1ddn4cyw?t=434) and slightly extended.

### The use of linear programming techniques

As already mentioned before, CP-SAT also utilizes the (dual) simplex algorithm and linear relaxations.
The linear relaxation is implemented as a propagator and potentially executed at every node in the search tree
but only at lowest priority. A significant difference to the application of linear relaxations in branch and bound
algorithms is that only some pivot iterations are performed (to make it faster). However, as there are likely
much deeper search trees and the warm-starts are utilized, the optimal linear relaxation may still be computed, just
deeper down the tree (note that for SAT-solving, the search tree is usually traversed DFS). At root level, even
cutting planes such as Gomory-Cuts are applied to improve the linear relaxation.

The linear relaxation is used for detecting infeasibility (IPs can actually be more powerful than simple SAT, at least
in theory), finding better bounds for the objective and variables, and also for making branching decisions (using the
linear relaxation's objective and the reduced costs).

The used Relaxation Induced Neighborhood Search RINS (LNS worker), a very successful heuristic, of course also uses
linear programming.

### The disadvantages of CP-SAT

CP-SAT is a very powerful solver, but it also has some disadvantages compared to other technique:

1. It is not as fast as a dedicated SAT-solver if you use it to solve SAT-formulas (but it is still pretty fast).
2. It is not as fast as a dedicated MIP-solver if you use it to solve classical MIP-problems (but it is still pretty fast).
3. It does not support continuous variables as MIP/LP-solvers do and the hacks to use them are not always very efficient.
4. It does not support lazy constraints or iterative model building as MIP/LP-solvers and some SAT-solvers do. This prevents the usage of some exponential sized models, which are common and important in Mixed Integer Programming.
5. As CP-SAT only has access to the Simplex-algorithm (and not interior point methods), it cannot use polynomial time algorithms for some classes of quadratic constraints (e.g., Second Order Cone). Gurobi, for example, can solve these constraints in polynomial time using the Barrier-algorithm.

CP-SAT might also exhibit inefficiency when confronted with certain constraints, such as modulo constraints.
However, it's noteworthy that I am not aware of any alternative solver capable of efficiently addressing these specific constraints.
At times, NP-hard problems inherently pose formidable challenges, leaving us with no alternative but to seek more manageable modeling approaches instead of looking for better solvers.

## Large Neighborhood Search

### The use of CP-SAT to create more powerful heuristics

CP-SAT can solve some small to medium-sized instances reasonably fast.
However, for some problems you need to solve larger instances that are beyond any of the
current solvers. You could now fall back to classical meta-heuristics such as genetic
algorithms or any algorithm with a fancy name that will impress managers, but actually
perform not much better than some greedy decisions (but because the algorithm is so
fancy, you don't have the resources to compare it to something else and no one will ever
know). Ok, you may have noticed the sarcasm and that I don't think very highly of most meta-heuristics, especially if they have fancy names.
The proliferation of complex sounding meta-heuristics, that are actually just some variation of existing algorithms (potentially even missing important elements of them), is actually a problem in the field of meta-heuristics, and mentioned as first point in the [Policies on Heuristic Search by the Springer Journal of Heuristics](https://www.springer.com/journal/10732/updates/17199246).
During my undergraduate years, I too ventured into creating my own intricate meta-heuristics. In hindsight, I recognize that these attempts were merely ineffectual adaptations of pre-existing concepts. I suspect that many individuals in our field have embarked on similar journeys at some stage in their academic pursuits.
However, in this section, I will show you
a technique that won't win you much awe, but is easy to implement as we again let a
solver, i.e., CP-SAT, do the hard work, and will probably perform much better than most
heuristics.

The problem with most meta-heuristics is, that they create for a given solution (pool) a
number of explicit(!) neighbored solutions and select from them the next solution (pool).
As one has to explicitly construct these solutions, only a limited number can be
considered. This number can be in the tens of thousands, but it has to be at a size where
each of them can be looked at individually. Note that this is also true for sampling
based approaches that create neighbored solutions from an arbitrarily large space, but
the samples that are considered will still be a small number. The idea of Large 
Neighborhood Search is to not have concrete solutions but to specify an auxiliary
optimization problem, e.g., allowing changes on a fixed number of variables, and let
a solver such as CP-SAT find the best next solution based on this auxiliary optimization
problem. This allows us to actually scan an exponential number of neighbored solutions
as we do not explicitly construct these solutions. You could also integrate this approach
into a genetic algorithm, where you use a solver to find the best combination of
solutions for the crossover or as a mutation.

> TODO: Continue. Provide concrete example....

## Further Material

Let me close this primer with some further references, that may come useful:

* You may have already been referred to the talk [Search is Dead, Long Live Proof by Peter Stuckey](TODO).
    * You can find [a recording](https://www.youtube.com/watch?v=lxiCHRFNgno) to nearly the same talk, which may be
      helpful because the slides miss the intermediate steps.
    * If you want to dig deeper, you also go
      to [the accompanying paper](https://people.eng.unimelb.edu.au/pstuckey/papers/cp09-lc.pdf).
    * This may be a little overwhelming if you are not familiar enough with SAT-solving.
* There is also [a talk of the developers of CP-SAT](https://youtu.be/lmy1ddn4cyw), which however is highly technical.
    * Gives more details on further tricks done by CP-SAT, on top of lazy clause generation.
    * The second part especially goes into details on the usage of LPs in CP-SAT. So if you are coming from that
      community, this talk will be fascinating for you.
* The slides for the course 'Solving Hard Problems in Practice' by Jediah Katz are pretty great to understand the
  techniques without any prior knowledge, however, they are currently no longer available online.
* [This blog](https://www.msoos.org/) gives some pretty nice insights into developing state of the art SAT-solvers.
* [Official Tutorial](https://developers.google.com/optimization/cp): The official tutorial is reasonably good, but
  somehow missing important information and it also seems like it is actually just updated from the previous, not so
  powerful, CP-solver.
* [Documentation](https://google.github.io/or-tools/python/ortools/sat/python/cp_model.html): The documentations give a
  good overview of the available functions but are often not extensively explained.
* [Sources](https://github.com/google/or-tools/tree/stable/ortools/sat): The sources actually contain a lot of
  information, once you know where to look. Especially a look into
  the [parameters](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto) can be very
  enlightening.
* [Model Building in Mathematical Programming by H. Paul Williams](https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330)
    * A book about modelling practical problems. Quite comprehensive with lots of tricks I didn't know about earlier.
  Be aware that too clever models are often hard to solve, so maybe it is not always a good thing to know too many
  tricks. A nice thing about this book is that the second half gives you a lot of real world examples and solutions.
    * Be aware that this book is about modelling, not solving. The latest edition is from 2013, the earliest from 1978.
  The math hasn't changed, but the capabilities and techniques of the solvers quite a lot.
