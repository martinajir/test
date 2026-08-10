"""
Simple Julia web server for the test repo.

Endpoints:
  GET /            -> plain text welcome message
  GET /health      -> JSON health check, e.g. {"status":"ok"}
  GET /jokes       -> a random pirate joke from pirate-jokes.txt as JSON

Run with:
    julia --project=. server.jl

Then visit http://localhost:8080/
"""

using HTTP
using JSON3

const PORT = parse(Int, get(ENV, "PORT", "8080"))
const JOKES_FILE = joinpath(@__DIR__, "pirate-jokes.txt")

"""Parse numbered jokes out of pirate-jokes.txt into a Vector{String}."""
function load_jokes()
    jokes = String[]
    isfile(JOKES_FILE) || return jokes
    for line in eachline(JOKES_FILE)
        m = match(r"^\d+\.\s*(.+)$", line)
        if m !== nothing
            push!(jokes, String(m.captures[1]))
        end
    end
    return jokes
end

function handle_root(::HTTP.Request)
    return HTTP.Response(200, "text/plain; charset=utf-8",
        "Hello from the Julia web server! Try /health or /jokes.\n")
end

function handle_health(::HTTP.Request)
    body = JSON3.write(Dict("status" => "ok"))
    return HTTP.Response(200, ["Content-Type" => "application/json"], body)
end

function handle_jokes(::HTTP.Request)
    jokes = load_jokes()
    joke = isempty(jokes) ? "No jokes found!" : rand(jokes)
    body = JSON3.write(Dict("joke" => joke))
    return HTTP.Response(200, ["Content-Type" => "application/json"], body)
end

function handle_not_found(::HTTP.Request)
    body = JSON3.write(Dict("error" => "not found"))
    return HTTP.Response(404, ["Content-Type" => "application/json"], body)
end

function router(req::HTTP.Request)
    path = HTTP.URI(req.target).path
    if req.method == "GET" && path == "/"
        return handle_root(req)
    elseif req.method == "GET" && path == "/health"
        return handle_health(req)
    elseif req.method == "GET" && path == "/jokes"
        return handle_jokes(req)
    else
        return handle_not_found(req)
    end
end

function main()
    println("Starting Julia web server on http://0.0.0.0:$PORT ...")
    HTTP.serve(router, "0.0.0.0", PORT)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
