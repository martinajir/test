#!/usr/bin/env julia
"""
A minimal HTTP webserver written in pure Julia using only the standard
library (Sockets). No external packages are required, so it can run with
just `julia server.jl` on any machine with Julia installed.

Routes:
  GET /            -> welcome message
  GET /health      -> health check JSON
  GET /jokes       -> a random pirate joke from pirate-jokes.txt
  GET /add?a=1&b=2 -> adds two numbers and returns JSON
"""

using Sockets

const PORT = parse(Int, get(ENV, "PORT", "8080"))
const JOKES_FILE = joinpath(@__DIR__, "pirate-jokes.txt")

# Extract numbered joke lines like "1. Why couldn't ..." from pirate-jokes.txt
function load_jokes()
    jokes = String[]
    if isfile(JOKES_FILE)
        for line in eachline(JOKES_FILE)
            m = match(r"^\d+\.\s*(.+)$", line)
            if m !== nothing
                push!(jokes, String(m.captures[1]))
            end
        end
    end
    isempty(jokes) && push!(jokes, "Why did the pirate cross the road? To get to the other tide!")
    return jokes
end

const JOKES = load_jokes()

function parse_query(qs::AbstractString)
    params = Dict{String,String}()
    for pair in split(qs, '&'; keepempty=false)
        kv = split(pair, '='; limit=2)
        key = String(kv[1])
        val = length(kv) > 1 ? String(kv[2]) : ""
        params[key] = val
    end
    return params
end

function parse_request_line(line::AbstractString)
    parts = split(line, ' ')
    length(parts) < 2 && return ("GET", "/", Dict{String,String}())
    method = String(parts[1])
    target = parts[2]
    path, qs = occursin('?', target) ? split(target, '?'; limit=2) : (target, "")
    query = isempty(qs) ? Dict{String,String}() : parse_query(qs)
    return (method, String(path), query)
end

function json_escape(s::AbstractString)
    replace(s, "\\" => "\\\\", "\"" => "\\\"")
end

function http_response(status::Int, status_text::String, body::String; content_type="application/json")
    headers = "HTTP/1.1 $status $status_text\r\n" *
              "Content-Type: $content_type; charset=utf-8\r\n" *
              "Content-Length: $(sizeof(body))\r\n" *
              "Connection: close\r\n\r\n"
    return headers * body
end

function handle_request(method::String, path::String, query::Dict{String,String})
    if path == "/"
        body = "{\"message\": \"Welcome to the Julia webserver!\"}"
        return http_response(200, "OK", body)
    elseif path == "/health"
        body = "{\"status\": \"ok\"}"
        return http_response(200, "OK", body)
    elseif path == "/jokes"
        joke = rand(JOKES)
        body = "{\"joke\": \"$(json_escape(joke))\"}"
        return http_response(200, "OK", body)
    elseif path == "/add"
        a = tryparse(Float64, get(query, "a", ""))
        b = tryparse(Float64, get(query, "b", ""))
        if a === nothing || b === nothing
            body = "{\"error\": \"Please provide numeric query params 'a' and 'b', e.g. /add?a=1&b=2\"}"
            return http_response(400, "Bad Request", body)
        end
        body = "{\"a\": $a, \"b\": $b, \"sum\": $(a + b)}"
        return http_response(200, "OK", body)
    else
        body = "{\"error\": \"Not Found\"}"
        return http_response(404, "Not Found", body)
    end
end

function handle_connection(sock)
    try
        line = readline(sock)
        if isempty(line)
            close(sock)
            return
        end
        method, path, query = parse_request_line(line)

        # Drain remaining headers (we don't need them for these simple routes).
        while !eof(sock)
            hline = readline(sock)
            isempty(hline) && break
        end

        response = handle_request(method, path, query)
        write(sock, response)
    catch e
        @warn "Error handling connection" exception = e
    finally
        close(sock)
    end
end

function main()
    server = listen(IPv4(0), PORT)
    println("Julia webserver listening on http://0.0.0.0:$PORT")
    println("Routes: /  /health  /jokes  /add?a=1&b=2")
    try
        while true
            sock = accept(server)
            @async handle_connection(sock)
        end
    finally
        close(server)
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
