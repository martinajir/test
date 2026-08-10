"""
Simple Julia web server for the test repo.

Endpoints:
  GET  /               -> plain text welcome message
  GET  /health         -> JSON health check, e.g. {"status":"ok"}
  GET  /jokes          -> a random pirate joke as JSON
  POST /jokes          -> add a new joke, body: {"joke": "..."}
  DELETE /jokes/{index} -> delete the joke at the given 0-based index
  GET  /recipes        -> all recipes (from README.md plus any added) as JSON
  GET  /recipes/{name} -> a single recipe by name (case-insensitive) as JSON
  POST /recipes        -> add a new recipe, body:
                           {"name": "...", "ingredients": [...], "instructions": [...]}
  DELETE /recipes/{name} -> delete the recipe with the given name (case-insensitive)

Run with:
    julia --project=. server.jl

Then visit http://localhost:8080/
"""

using HTTP
using JSON3

const PORT = parse(Int, get(ENV, "PORT", "8080"))
const JOKES_FILE = joinpath(@__DIR__, "pirate-jokes.txt")
const README_FILE = joinpath(@__DIR__, "README.md")

# In-memory, thread-safe state. Seeded from disk at startup; POST endpoints
# append to these vectors under `STATE_LOCK` so concurrent requests are safe.
const STATE_LOCK = ReentrantLock()
const JOKES = String[]
const RECIPES = Vector{Dict{String,Any}}()

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

"""
Parse `## Recipe: Name` sections out of README.md into a Vector of
Dict("name" => ..., "ingredients" => [...], "instructions" => [...]).
"""
function load_recipes()
    recipes = Dict{String,Any}[]
    isfile(README_FILE) || return recipes

    text = read(README_FILE, String)
    # Split on recipe headings, keeping the heading with its section.
    sections = split(text, r"(?=^## Recipe: )"m)
    for section in sections
        m = match(r"^## Recipe: (.+)$"m, section)
        m === nothing && continue
        name = strip(m.captures[1])

        ingredients = String[]
        ing_match = match(r"### Ingredients\s*\n(.*?)(?=\n### |\z)"s, section)
        if ing_match !== nothing
            for line in split(ing_match.captures[1], '\n')
                im = match(r"^-\s*(.+)$", strip(line))
                im !== nothing && push!(ingredients, String(im.captures[1]))
            end
        end

        instructions = String[]
        instr_match = match(r"### Instructions\s*\n(.*?)(?=\n## |\z)"s, section)
        if instr_match !== nothing
            for line in split(instr_match.captures[1], '\n')
                sm = match(r"^\d+\.\s*(.+)$", strip(line))
                sm !== nothing && push!(instructions, String(sm.captures[1]))
            end
        end

        push!(recipes, Dict(
            "name" => String(name),
            "ingredients" => ingredients,
            "instructions" => instructions,
        ))
    end
    return recipes
end

function json_response(status::Int, data)
    return HTTP.Response(status, ["Content-Type" => "application/json"], JSON3.write(data))
end

"""Parse the JSON request body; returns `nothing` (and leaves it to the
caller to respond 400) if the body is missing or not valid JSON."""
function parse_json_body(req::HTTP.Request)
    isempty(req.body) && return nothing
    try
        return JSON3.read(String(req.body))
    catch
        return nothing
    end
end

function handle_root(::HTTP.Request)
    return HTTP.Response(200, "text/plain; charset=utf-8",
        "Hello from the Julia web server! Try /health, /jokes, or /recipes.\n")
end

function handle_health(::HTTP.Request)
    return json_response(200, Dict("status" => "ok"))
end

function handle_get_jokes(::HTTP.Request)
    joke = lock(STATE_LOCK) do
        isempty(JOKES) ? "No jokes found!" : rand(JOKES)
    end
    return json_response(200, Dict("joke" => joke))
end

function handle_post_jokes(req::HTTP.Request)
    body = parse_json_body(req)
    if body === nothing || !haskey(body, :joke) || isempty(strip(String(body.joke)))
        return json_response(400, Dict("error" => "expected JSON body with a non-empty \"joke\" string"))
    end
    joke = String(body.joke)
    lock(STATE_LOCK) do
        push!(JOKES, joke)
    end
    return json_response(201, Dict("joke" => joke))
end

function handle_get_recipes(::HTTP.Request)
    recipes = lock(STATE_LOCK) do
        copy(RECIPES)
    end
    return json_response(200, Dict("recipes" => recipes))
end

function handle_get_recipe(::HTTP.Request, name::AbstractString)
    decoded = HTTP.URIs.unescapeuri(name)
    recipe = lock(STATE_LOCK) do
        idx = findfirst(r -> lowercase(r["name"]) == lowercase(decoded), RECIPES)
        idx === nothing ? nothing : RECIPES[idx]
    end
    if recipe === nothing
        return json_response(404, Dict("error" => "recipe not found: $decoded"))
    end
    return json_response(200, recipe)
end

function handle_post_recipes(req::HTTP.Request)
    body = parse_json_body(req)
    if body === nothing || !haskey(body, :name) || isempty(strip(String(body.name)))
        return json_response(400, Dict("error" => "expected JSON body with a non-empty \"name\" string"))
    end

    name = String(body.name)
    ingredients = haskey(body, :ingredients) ? String.(collect(body.ingredients)) : String[]
    instructions = haskey(body, :instructions) ? String.(collect(body.instructions)) : String[]

    recipe = Dict{String,Any}(
        "name" => name,
        "ingredients" => ingredients,
        "instructions" => instructions,
    )

    lock(STATE_LOCK) do
        idx = findfirst(r -> lowercase(r["name"]) == lowercase(name), RECIPES)
        if idx === nothing
            push!(RECIPES, recipe)
        else
            RECIPES[idx] = recipe
        end
    end
    return json_response(201, recipe)
end

function handle_delete_recipe(::HTTP.Request, name::AbstractString)
    decoded = HTTP.URIs.unescapeuri(name)
    found = lock(STATE_LOCK) do
        idx = findfirst(r -> lowercase(r["name"]) == lowercase(decoded), RECIPES)
        if idx === nothing
            false
        else
            deleteat!(RECIPES, idx)
            true
        end
    end
    if !found
        return json_response(404, Dict("error" => "recipe not found: $decoded"))
    end
    return HTTP.Response(204)
end

function handle_delete_joke(::HTTP.Request, index_str::AbstractString)
    index = tryparse(Int, index_str)
    if index === nothing
        return json_response(400, Dict("error" => "expected an integer index, got: $index_str"))
    end
    found = lock(STATE_LOCK) do
        if index < 0 || index >= length(JOKES)
            false
        else
            deleteat!(JOKES, index + 1)  # index is 0-based, JOKES is 1-based
            true
        end
    end
    if !found
        return json_response(404, Dict("error" => "joke index out of range: $index"))
    end
    return HTTP.Response(204)
end

function handle_not_found(::HTTP.Request)
    return json_response(404, Dict("error" => "not found"))
end

function router(req::HTTP.Request)
    path = HTTP.URI(req.target).path
    method = req.method

    if method == "GET" && path == "/"
        return handle_root(req)
    elseif method == "GET" && path == "/health"
        return handle_health(req)
    elseif method == "GET" && path == "/jokes"
        return handle_get_jokes(req)
    elseif method == "POST" && path == "/jokes"
        return handle_post_jokes(req)
    elseif method == "DELETE" && startswith(path, "/jokes/")
        index_str = path[length("/jokes/")+1:end]
        return handle_delete_joke(req, index_str)
    elseif method == "GET" && path == "/recipes"
        return handle_get_recipes(req)
    elseif method == "POST" && path == "/recipes"
        return handle_post_recipes(req)
    elseif method == "DELETE" && startswith(path, "/recipes/")
        name = path[length("/recipes/")+1:end]
        return handle_delete_recipe(req, name)
    elseif method == "GET" && startswith(path, "/recipes/")
        name = path[length("/recipes/")+1:end]
        return handle_get_recipe(req, name)
    else
        return handle_not_found(req)
    end
end

function main()
    append!(JOKES, load_jokes())
    append!(RECIPES, load_recipes())
    println("Starting Julia web server on http://0.0.0.0:$PORT ...")
    HTTP.serve(router, "0.0.0.0", PORT)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
