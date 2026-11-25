#pragma once

// AngelScript releases before 2.31 test types with std::has_trivial_* traits. C++11 deprecated them
// and current standard libraries removed them. This header, force-included for those releases only,
// maps each one to its replacement so the unmodified official sources compile.

#include <type_traits>

namespace std
{
template <class T> struct has_trivial_default_constructor : is_trivially_default_constructible<T> {};
template <class T> struct has_trivial_copy_constructor : is_trivially_copy_constructible<T> {};
template <class T> struct has_trivial_copy_assign : is_trivially_copy_assignable<T> {};
template <class T> struct has_trivial_destructor : is_trivially_destructible<T> {};
}
