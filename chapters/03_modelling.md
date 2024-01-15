## Modelling

CP-SAT provides us with much more modelling options than the classical
MIP-solver. Instead of just the classical linear constraints (<=, ==, >=), we
have various advanced constraints such as `AllDifferent` or
`AddMultiplicationEquality`. This spares you the burden of modelling the logic
only with linear constraints, but also makes the interface more extensive.
Additionally, you have to be aware that not all constraints are equally
efficient. The most efficient constraints are linear or boolean constraints.
Constraints such as `AddMultiplicationEquality` can be significantly(!!!) more
expensive.

> **If you are coming from the MIP-world, you should not overgeneralize your
> experience** to CP-SAT as the underlying techniques are different. It does not
> rely on the linear relaxation as much as MIP-solvers do. Thus, you can often
> use modelling techniques that are not efficient in MIP-solvers, but perform
> reasonably well in CP-SAT. For example, I had a model that required multiple
> absolute values and performed significantly better in CP-SAT than in Gurobi
> (despite a manual implementation with relatively tight big-M values).

This primer does not have the space to teach about building good models. In the
following, we will primarily look onto a selection of useful constraints. If you
want to learn how to build models, you could take a look into the book
[Model Building in Mathematical Programming by H. Paul Williams](https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330)
which covers much more than you probably need, including some actual
applications. This book is of course not for CP-SAT, but the general techniques
and ideas carry over. However, it can also suffice to simply look on some other
models and try some things out. If you are completely new to this area, you may
want to check out modelling for the MIP-solver Gurobi in this
[video course](https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9).
Remember that many things are similar to CP-SAT, but not everything (as already
mentioned, CP-SAT is especially interesting for the cases where a MIP-solver
fails).

The following part does not cover all constraints. You can get a complete
overview by looking into the
[official documentation](https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel).
Simply go to `CpModel` and check out the `AddXXX` and `NewXXX` methods.

Resources on mathematical modelling (not CP-SAT specific):

- [Math Programming Modeling Basics by Gurobi](https://www.gurobi.com/resources/math-programming-modeling-basics/):
  Get the absolute basics.
- [Modeling with Gurobi Python](https://www.youtube.com/playlist?list=PLHiHZENG6W8CezJLx_cw9mNqpmviq3lO9):
  A video course on modelling with Gurobi. The concepts carry over to CP-SAT.
- [Model Building in Mathematical Programming by H. Paul Williams](https://www.wiley.com/en-us/Model+Building+in+Mathematical+Programming%2C+5th+Edition-p-9781118443330):
  A complete book on mathematical modelling.

### Variables

There are two important types of variables in CP-SAT: Booleans and Integers
(which are actually converted to Booleans, but more on this later). There are
also, e.g.,
[interval variables](https://developers.google.com/optimization/reference/python/sat/python/cp_model#intervalvar),
but they are not as important and can be modelled easily with integer variables.
For the integer variables, you have to specify a lower and an upper bound.

```python
# integer variable z with bounds -100 <= z <= 100
z = model.NewIntVar(-100, 100, "z")
# boolean variable b
b = model.NewBoolVar("b")
# implicitly available negation of b:
not_b = b.Not()  # will be 1 if b is 0 and 0 if b is 1
```

> Having tight bounds on the integer variables can make a huge impact on the
> performance. It may be useful to run some optimization heuristics beforehand
> to get some bounds. Reducing it by a few percent can already pay off for some
> problems.

There are no continuous/floating point variables (or even constants) in CP-SAT:
If you need floating point numbers, you have to approximate them with integers
by some resolution. For example, you could simply multiply all values by 100 for
a step size of 0.01. A value of 2.35 would then be represented by 235. This
_could_ probably be implemented in CP-SAT directly, but doing it explicitly is
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
[./examples/add_no_overlap_2d_scaling.ipynb](./examples/add_no_overlap_2d_scaling.ipynb)
for the code. If you have a problem with a lot of continuous variables, such as
[network flow problems](https://en.wikipedia.org/wiki/Network_flow_problem), you
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

### Objectives

Not every problem actually has an objective, sometimes you only need to find a
feasible solution. CP-SAT is pretty good at doing that (MIP-solvers are often
not). However, CP-SAT can also optimize pretty well (older constraint
programming solver cannot, at least in my experience). You can minimize or
maximize a linear expression (use auxiliary variables and constraints to model
more complicated expressions).

You can specify the objective function by calling `model.Minimize` or
`model.Maximize` with a linear expression.

```python
model.Maximize(30 * x + 50 * y)
```

Let us look on how to model more complicated expressions, using boolean
variables and generators.

```python
x_vars = [model.NewBoolVar(f"x{i}") for i in range(10)]
model.Minimize(
    sum(i * x_vars[i] if i % 2 == 0 else i * x_vars[i].Not() for i in range(10))
)
```

This objective evaluates to

$$
\min \sum_{i=0}^{9} i\cdot x_i \text{ if } i \text{ is even else } i\cdot \neg x_i
$$

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

To implement non-linear objectives, you can use auxiliary variables and
constraints. For example, you can create a variable that is the absolute value
of another variable and then use this variable in the objective.

```python
abs_x = model.NewIntVar(0, 100, "|x|")
model.AddAbsEquality(target=abs_x, expr=x)
model.Minimize(abs_x)
```

The available constraints are discussed next.

### Linear Constraints

These are the classical constraints also used in linear optimization. Remember
that you are still not allowed to use floating point numbers within it. Same as
for linear optimization: You are not allowed to multiply a variable with
anything else than a constant and also not to apply any further mathematical
operations.

```python
model.Add(10 * x + 15 * y <= 10)
model.Add(x + z == 2 * y)

# This one actually isn't linear but still works.
model.Add(x + y != z)

# For <, > you can simply use <= and -1 because we are working on integers.
model.Add(x <= z - 1)  # x < z
```

Note that `!=` can be expected slower than the other (`<=`, `>=`, `==`)
constraints, because it is not a linear constraint. If you have a set of
mutually `!=` variables, it is better to use `AllDifferent` (see below) than to
use the explicit `!=` constraints.

> :warning: If you use intersecting linear constraints, you may get problems
> because the intersection point needs to be integral. There is no such thing as
> a feasibility tolerance as in Mixed Integer Programming-solvers, where small
> deviations are allowed. The feasibility tolerance in MIP-solvers allows, e.g.,
> 0.763445 == 0.763439 to still be considered equal to counter numerical issues
> of floating point arithmetic. In CP-SAT, you have to make sure that values can
> match exactly.

### Logical Constraints (Propositional Logic)

You can actually model logical constraints also as linear constraints, but it
may be advantageous to show your intent:

```python
b1 = model.NewBoolVar("b1")
b2 = model.NewBoolVar("b2")
b3 = model.NewBoolVar("b3")

model.AddBoolOr(b1, b2, b3)  # b1 or b2 or b3 (at least one)
model.AddBoolAnd(b1, b2.Not(), b3.Not())  # b1 and not b2 and not b3 (all)
model.AddBoolXOr(b1, b2, b3)  # b1 xor b2 xor b3
model.AddImplication(b1, b2)  # b1 -> b2
```

In this context you could also mention `AddAtLeastOne`, `AddAtMostOne`, and
`AddExactlyOne`, but these can also be modelled as linear constraints.

### Conditional Constraints

Linear constraints (Add), BoolOr, and BoolAnd support being activated by a
condition. This is not only a very helpful constraint for many applications, but
it is also a constraint that is highly inefficient to model with linear
optimization ([Big M Method](https://en.wikipedia.org/wiki/Big_M_method)). My
current experience shows that CP-SAT can work much more efficiently with this
kind of constraint. Note that you only can use a boolean variable and not
directly add an expression, i.e., maybe you need to create an auxiliary
variable.

```python
model.Add(x + z == 2 * y).OnlyEnforceIf(b1)
model.Add(x + z == 10).OnlyEnforceIf([b2, b3.Not()])  # only enforce if b2 AND NOT b3
```

### AllDifferent

A constraint that is often seen in Constraint Programming, but I myself was
always able to deal without it. Still, you may find it important. It forces all
(integer) variables to have a different value.

`AllDifferent` is actually the only constraint that may use a domain based
propagator (if it is not a permutation)
[[source](https://youtu.be/lmy1ddn4cyw?t=624)]

```python
model.AddAllDifferent(x, y, z)

# You can also add a constant to the variables.
vars = [model.NewIntVar(0, 10) for i in range(10)]
model.AddAllDifferent(x + i for i, x in enumerate(vars))
```

The [N-queens](https://developers.google.com/optimization/cp/queens) example of
the official tutorial makes use of this constraint.

There is a big caveat with this constraint: CP-SAT now has a preprocessing step
that automatically tries to infer large `AllDifferent` constraints from sets of
mutual `!=` constraints. This inference equals the NP-hard Edge Clique Cover
problem, thus, is not a trivial task. If you add an `AllDifferent` constraint
yourself, CP-SAT will assume that you already took care of this inference and
will skip this step. Thus, adding a single `AllDifferent` constraint can make
your model significantly slower, if you also use `!=` constraints. If you do not
use `!=` constraints, you can safely use `AllDifferent` without any performance
penalty. You may also want to use `!=` instead of `AllDifferent` if you apply it
to overlapping sets of variables without proper optimization, because then
CP-SAT will do the inference for you.

In [./examples/add_all_different.ipynb](./examples/add_all_different.ipynb) you
can find a quick experiment based on the graph coloring problem. In the graph
coloring problem, the colors of two adjacent vertices have to be different. This
can be easily modelled by `!=` or `AllDifferent` constraints on every edge.
Using `!=`, we can solve the example graph in around 5 seconds. If we use
`AllDifferent`, it takes more than 5 minutes. If we manually disable the
`AllDifferent` inference, it also takes more than 5 minutes. Same if we add just
a single `AllDifferent` constraint. Thus, if you use `AllDifferent` do it
properly on large sets, or use `!=` constraints and let CP-SAT infer the
`AllDifferent` constraints for you.

Maybe CP-SAT will allow you to use `AllDifferent` without any performance
penalty in the future, but for now, you have to be aware of this. See also
[the optimization parameter documentation](https://github.com/google/or-tools/blob/1d696f9108a0ebfd99feb73b9211e2f5a6b0812b/ortools/sat/sat_parameters.proto#L542).

### Absolute Values and Max/Min

Two often occurring and important operators are absolute values as well as
minimum and maximum values. You cannot use operators directly in the
constraints, but you can use them via an auxiliary variable and a dedicated
constraint. These constraints are reasonably efficient in my experience.

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

A big nono in linear optimization (the most successful optimization area) are
multiplication of variables (because this would no longer be linear, right...).
Often we can linearize the model by some tricks and tools like Gurobi are also
able to do some non-linear optimization ( in the end, it is most often
translated to a less efficient linear model again). CP-SAT can also work with
multiplication and modulo of variables, again as constraint not as operation. So
far, I have not made good experience with these constraints, i.e., the models
end up being slow to solve, and would recommend to only use them if you really
need them and cannot find a way around them.

```python
xyz = model.NewIntVar(-100 * 100 * 100, 100**3, "x*y*z")
model.AddMultiplicationEquality(xyz, [x, y, z])  # xyz = x*y*z
model.AddModuloEquality(x, y, 3)  # x = y % 3
```

> :warning: The documentation indicates that multiplication of more than two
> variables is supported, but I got an error when trying it out. I have not
> investigated this further, as I would expect it to be slow anyway.

### Circuit/Tour-Constraints

The
[Traveling Salesman Problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
or Hamiltonicity Problem are important and difficult problems that occur as
subproblem in many contexts. For solving the classical TSP, you should use the
extremely powerful solver
[Concorde](https://www.math.uwaterloo.ca/tsp/concorde.html). There is also a
separate [part in ortools](https://developers.google.com/optimization/routing)
dedicated to routing. If it is just a subproblem, you can add a simple
constraint by encoding the allowed edges as triples of start vertex index,
target vertex index, and literal/variable. Note that this is using directed
edges/arcs. By adding a triple (v,v,var), you can allow CP-SAT to skip the
vertex v.

> If the tour-problem is the fundamental part of your problem, you may be better
> served with using a Mixed Integer Programming solver. Don't expect to solve
> tours much larger than 250 vertices with CP-SAT.

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
```

    Tour: [(0, 1), (2, 0), (3, 2), (1, 3)]

You can use this constraint very flexibly for many tour problems. We added three
examples:

- [./examples/add_circuit.py](./examples/add_circuit.py): The example above,
  slightly extended. Find out how large you can make the graph.
- [./examples/add_circuit_budget.py](./examples/add_circuit_budget.py): Find the
  largest tour with a given budget. This will be a bit more difficult to solve.
- [./examples/add_circuit_multi_tour.py](./examples/add_circuit_multi_tour.py):
  Allow $k$ tours, which in sum need to be minimal and cover all vertices.

The most powerful TSP-solver _concorde_ uses a linear programming based
approach, but with a lot of additional techniques to improve the performance.
The book _In Pursuit of the Traveling Salesman_ by William Cook may have already
given you some insights. For more details, you can also read the more advanced
book _The Traveling Salesman Problem: A Computational Study_ by Applegate,
Bixby, Chvatál, and Cook. If you need to solve some variant, MIP-solvers (which
could be called a generalization of that approach) are known to perform well
using the
[Dantzig-Fulkerson-Johnson Formulation](https://en.wikipedia.org/wiki/Travelling_salesman_problem#Dantzig%E2%80%93Fulkerson%E2%80%93Johnson_formulation).
This model is theoretically exponential, but using lazy constraints (which are
added when needed), it can be solved efficiently in practice. The
[Miller-Tucker-Zemlin formulation](https://en.wikipedia.org/wiki/Travelling_salesman_problem#Miller%E2%80%93Tucker%E2%80%93Zemlin_formulation[21])
allows a small formulation size, but is bad in practice with MIP-solvers due to
its weak linear relaxations. Because CP-SAT does not allow lazy constraints, the
Danzig-Fulkerson-Johnson formulation would require many iterations and a lot of
wasted resources. As CP-SAT does not suffer as much from weak linear relaxations
(replacing Big-M by logic constraints, such as `OnlyEnforceIf`), the
Miller-Tucker-Zemlin formulation may be an option in some cases, though a simple
experiment (see below) shows a similar performance as the iterative approach.
When using `AddCircuit`, CP-SAT will actually use the LP-technique for the
linear relaxation (so using this constraint may really help, as otherwise CP-SAT
will not know that your manual constraints are actually a tour with a nice
linear relaxation), and probably has the lazy constraints implemented
internally. Using the `AddCircuit` constraint is thus highly recommendable for
any circle or path constraints.

In
[./examples/add_circuit_comparison.ipynb](./examples/add_circuit_comparison.ipynb),
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
`AddCircuit` constraint.

> These are all naive implementations, and the benchmark is not very rigorous.
> These values are only meant to give you a rough idea of the performance.
> Additionally, this benchmark was regarding proving _optimality_. The
> performance in just optimizing a tour could be different. The numbers could
> also look different for differently generated instances. You can find a more
> detailed benchmark in the later section on proper evaluation.

Here is the performance of `AddCircuit` for the TSP on some instances (rounded
eucl. distance) from the TSPLIB with a time limit of 90 seconds.

| Instance | # nodes | runtime | lower bound | objective | opt. gap |
| :------- | ------: | ------: | ----------: | --------: | -------: |
| att48    |      48 |    0.47 |       33522 |     33522 |        0 |
| eil51    |      51 |    0.69 |         426 |       426 |        0 |
| st70     |      70 |     0.8 |         675 |       675 |        0 |
| eil76    |      76 |    2.49 |         538 |       538 |        0 |
| pr76     |      76 |   54.36 |      108159 |    108159 |        0 |
| kroD100  |     100 |    9.72 |       21294 |     21294 |        0 |
| kroC100  |     100 |    5.57 |       20749 |     20749 |        0 |
| kroB100  |     100 |     6.2 |       22141 |     22141 |        0 |
| kroE100  |     100 |    9.06 |       22049 |     22068 |        0 |
| kroA100  |     100 |    8.41 |       21282 |     21282 |        0 |
| eil101   |     101 |    2.24 |         629 |       629 |        0 |
| lin105   |     105 |    1.37 |       14379 |     14379 |        0 |
| pr107    |     107 |     1.2 |       44303 |     44303 |        0 |
| pr124    |     124 |    33.8 |       59009 |     59030 |        0 |
| pr136    |     136 |   35.98 |       96767 |     96861 |        0 |
| pr144    |     144 |   21.27 |       58534 |     58571 |        0 |
| kroB150  |     150 |   58.44 |       26130 |     26130 |        0 |
| kroA150  |     150 |   90.94 |       26498 |     26977 |       2% |
| pr152    |     152 |   15.28 |       73682 |     73682 |        0 |
| kroA200  |     200 |   90.99 |       29209 |     29459 |       1% |
| kroB200  |     200 |   31.69 |       29437 |     29437 |        0 |
| pr226    |     226 |   74.61 |       80369 |     80369 |        0 |
| gil262   |     262 |   91.58 |        2365 |      2416 |       2% |
| pr264    |     264 |   92.03 |       49121 |     49512 |       1% |
| pr299    |     299 |   92.18 |       47709 |     49217 |       3% |
| linhp318 |     318 |   92.45 |       41915 |     52032 |      19% |
| lin318   |     318 |   92.43 |       41915 |     52025 |      19% |
| pr439    |     439 |   94.22 |      105610 |    163452 |      35% |

### Array operations

You can even go completely bonkers and work with arrays in your model. The
element at a variable index can be accessed via an `AddElement` constraint.

The second constraint is actually more of a stable matching in array form. For
two arrays of variables $v,w, |v|=|w|$, it requires
$v[i]=j \Leftrightarrow w[j]=i \quad \forall i,j \in 0,\ldots,|v|-1$. Note that
this restricts the values of the variables in the arrays to $0,\ldots, |v|-1$.

```python
# ai = [x,y,z][i]  assign ai the value of the i-th entry.
ai = model.NewIntVar(-100, 100, "a[i]")
i = model.NewIntVar(0, 2, "i")
model.AddElement(index=i, variables=[x, y, z], target=ai)

model.AddInverse([x, y, z], [z, y, x])
```

### Interval Variables and No-Overlap Constraints

CP-SAT also supports interval variables and corresponding constraints. These are
important for scheduling and packing problems. There are simple no-overlap
constraints for intervals for one-dimensional and two-dimensional intervals. In
two-dimensional intervals, only one dimension is allowed to overlap, i.e., the
other dimension has to be disjoint. This is essentially rectangle packing. Let
us see how we can model a simple 2-dimensional packing problem. Note that
`NewIntervalVariable` may indicate a new variable, but it is actually a
constraint container in which you have to insert the classical integer
variables. This constraint container is required, e.g., for the no-overlap
constraint.

```python
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
```

> The keywords `start` may be named `begin` in some versions of ortools.

See [this notebook](./examples/add_no_overlap_2d.ipynb) for the full example.

There is also the option for optional intervals, i.e., intervals that may be
skipped. This would allow you to have multiple containers or do a knapsack-like
packing.

The resolution seems to be quite important for this problem, as mentioned
before. The following table shows the runtime for different resolutions (the
solution is always the same, just scaled).

| Resolution | Runtime |
| ---------- | ------- |
| 1x         | 0.02s   |
| 10x        | 0.7s    |
| 100x       | 7.6s    |
| 1000x      | 75s     |
| 10_000x    | >15min  |

See [this notebook](../examples/add_no_overlap_2d_scaling.ipynb) for the full
example.

However, while playing around with less documented features, I noticed that the
performance can be improved drastically with the following parameters:

```python
solver.parameters.use_energetic_reasoning_in_no_overlap_2d = True
solver.parameters.use_timetabling_in_no_overlap_2d = True
solver.parameters.use_pairwise_reasoning_in_no_overlap_2d = True
```

Instances that could not be solved in 15 minutes before, can now be solved in
less than a second. This of course does not apply for all instances, but if you
are working with this constraint, you may want to jiggle with these parameters
if it struggles with solving your instances.

### There is more

CP-SAT has even more constraints, but I think I covered the most important ones.
If you need more, you can check out the
[official documentation](https://developers.google.com/optimization/reference/python/sat/python/cp_model#cp_model.CpModel).


