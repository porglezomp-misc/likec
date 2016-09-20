Given an input module

    (module
    (include math.h)

    (export length)
    (fn (length (v vec3)) double
      (return (sqrt (dot v v))))

    (fn (dot (a vec3) (b vec3)) double
      (return (+ (* a.x b.x)
                 (* a.y b.y)
                 (* a.z b.z))))

    (export line)
    (struct line
      (begin vec3)
      (end vec3))

    (export vec3)
    (struct vec3
      (x double)
      (y double)
      (z double))

    (export particle (abstract))
    (struct particle
      (pos vec3)
      (vel vec3)
      (mass double))

    (export particle_system)
    (struct particle_system
      (particles (ptr! particle))
      (int count)))

we need to do a few things.
We can validate that the type dependencies are well formed:
In this case we generate a dependency graph of the types, `line` and `particle` both rely on `vec3` so it has to come before either of them.
Since `particle_system` depends on `particle` through a pointer, it's safe to place them in any order as long as the type has been forward declared.
Since there are no dependency cycles, everything is fine.

Next we need to check the export soundness.
Any type that is concretely exported must rely only on other types that are exported.
For example, since `line` is exported, `vec3` must be exported (it is).
Furthermore, concrete types cannot contain abstract types, but they can contain pointers to abstract types.
Even though `particle` is abstractly exported, it's fine because `particle_system` only depends on it through a particle.
Any exported function has the same requirements as a struct, if it takes a struct as an argument by value or returns it by value then that struct must be exported concretely.
If it does so by pointer then it must at least be exported abstractly.
For our example module all of these criteria are satisfied.

We can construct the signature of a module

    (signature

    (fn (length (v vec3)) double)

    (struct line
      (begin vec3)
      (end vec3))

    (struct vec3
      (x double)
      (y double)
      (z double))

    (struct particle)
    (struct particle_system
      (particles (ptr! particle))
      (int count)))

- The signature of a module is the signature of every exported member.
- The signature of an abstract struct is just `(struct <name>)`.
- The signature of a concrete struct is the whole struct definition.
- For a function the signature is `(fn (<name> (<arg-name> <arg-type>)*) <ret>)`.

In order to generate the C implementation and header for the module, we need to sort the declarations so they come in the dependency order.
Performing a topological sort on the dependency graph with the edges reversed produces the ordering we want.
We insert an abstract declaration of every type at the top, then the definition of all concrete types.
After, we place the declarations for every function, and if there are implementations for functions we place them last.

What follows is the code generated for the module signatures.

    typedef struct line line;
    typedef struct vec3 vec3;
    typedef struct particle particle;
    typedef struct particle_system particle_system;

    struct vec3 {
      double x;
      double y;
      double z;
    };

    struct line {
      vec3 begin;
      vec3 end;
    };

    struct particle_system {
      particle *particles;
      int count;
    };

    double length(vec3 v);
