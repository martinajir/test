#!/usr/bin/env julia
"""
A simple web server for the `test` repo, built with HTTP.jl.

Endpoints:
  GET /            - welcome page with a list of available routes
  GET /health       - health check, returns {"status": "ok"}
  GET /jokes        - a random pirate joke from pirate-jokes.txt
  GET /add?a=1&b=2  - adds two numbers (query params `a` and `b`)

Run with:
  julia --project=. -e 'import Pkg; Pkg.instantiate()'
  julia --project=. server.jl

Then visit http://localhost:8080/
"""

using HTTP
using JSON3

const PORT = parse(Int, get(ENV, "PORT", "8080"))
const JOKES_FILE = joinpath(@__DIR__, "pirate-jokes.txt")

"""Parse pirate-jokes.txt into a vector of joke strings."""
function load_jokes()
    jokes = String[]
    if isfile(JOKES_FILE)
        for line in eachline(JOKES_FILE)
            m = match(r"^\d+\.\s+(.*)$", line)
            if m !== nothing
                push!(jokes, m.captures[1])
            end
        end
    end
    isempty(jokes) && push!(jokes, "Why couldn't the pirate play cards? Because he was sitting on the deck!")
    return jokes
end

const JOKES = load_jokes()

json_response(data; status::Int=200) =
    HTTP.Response(status, ["Content-Type" => "application/json"], JSON3.write(data))

function handle_root(::HTTP.Request)
    body = """
    <html>
    <head><title>test - Julia web server</title></head>
    <body>
        <h1>Ahoy! Welcome to the Julia-powered test server</h1>
        <p>Available endpoints:</p>
        <ul>
            <li><a href="/health">GET /health</a> - health check</li>
            <li><a href="/jokes">GET /jokes</a> - a random pirate joke</li>
            <li><a href="/add?a=2&b=3">GET /add?a=2&b=3</a> - add two numbers</li>
        </ul>
    </body>
    </html>
    """
    return HTTP.Response(200, ["Content-Type" => "text/html"], body)
end

handle_health(::HTTP.Request) = json_response(Dict("status" => "ok"))

function handle_jokes(::HTTP.Request)
    return json_response(Dict("joke" => rand(JOKES)))
end

function handle_add(req::HTTP.Request)
    params = HTTP.queryparams(HTTP.URI(req.target))
    if !haskey(params, "a") || !haskey(params, "b")
        return json_response(Dict("error" => "missing query params 'a' and/or 'b'"); status=400)
    end
    try
        a = parse(Float64, params["a"])
        b = parse(Float64, params["b"])
        return json_response(Dict("a" => a, "b" => b, "sum" => a + b))
    catch
        return json_response(Dict("error" => "'a' and 'b' must be numbers"); status=400)
    end
end

function router(req::HTTP.Request)
    target = HTTP.URI(req.target).path
    if target == "/" && req.method == "GET"
        return handle_root(req)
    elseif target == "/health" && req.method == "GET"
        return handle_health(req)
    elseif target == "/jokes" && req.method == "GET"
        return handle_jokes(req)
    elseif target == "/add" && req.method == "GET"
        return handle_add(req)
    else
        return json_response(Dict("error" => "not found"); status=404)
    end
end

function main()
    println("Starting server on http://0.0.0.0:$PORT ...")
    HTTP.serve(router, "0.0.0.0", PORT)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
