#!/usr/bin/env julia

function read_numbers()
    if length(ARGS) == 2
        return parse(Float64, ARGS[1]), parse(Float64, ARGS[2])
    end

    print("Enter the first number: ")
    first = parse(Float64, readline())
    print("Enter the second number: ")
    second = parse(Float64, readline())
    return first, second
end

first, second = read_numbers()
println("The sum of $first and $second is $(first + second)")
