import type { Track } from "@/types";

export type QueryNode =
    | { type: "equals"; key: string; value: string }
    | { type: "notEquals"; key: string; value: string }
    | { type: "contains"; key: string; value: string }
    | { type: "notContains"; key: string; value: string }
    | { type: "less"; key: string; value: number }
    | { type: "greater"; key: string; value: number }
    | { type: "lessOrEqual"; key: string; value: number }
    | { type: "greaterOrEqual"; key: string; value: number }
    | { type: "not"; child: QueryNode }
    | { type: "and"; left: QueryNode; right: QueryNode }
    | { type: "or"; left: QueryNode; right: QueryNode };

function removeQuotes(value: string): string {
    if (
        (value.startsWith("'") && value.endsWith("'")) ||
        (value.startsWith('"') && value.endsWith('"'))
    ) {
        return value.slice(1, -1);
    }
    return value;
}

class QueryParser {
    private tokens: string[] = [];
    private pos = 0;

    parse(query: string): QueryNode | null {
        if (!query.trim()) {
            return null;
        }

        this.tokens = this.tokenize(query);
        this.pos = 0;
        return this.parseOr();
    }

    private tokenize(query: string): string[] {
        const tokens: string[] = [];
        let i = 0;

        while (i < query.length) {
            // Skip whitespace
            if (/\s/.test(query[i])) {
                i++;
                continue;
            }

            // Handle parentheses
            if (query[i] === "(" || query[i] === ")") {
                tokens.push(query[i]);
                i++;
                continue;
            }

            // Handle quoted strings - look for key='value' or key="value"
            const quotedMatch = query
                .substring(i)
                .match(/^(\w+)(!~|!?=|~)(['"])/);
            if (quotedMatch) {
                const key = quotedMatch[1];
                const operator = quotedMatch[2];
                const quote = quotedMatch[3];
                const startQuote = i + key.length + operator.length; // position after operator
                const endQuote = query.indexOf(quote, startQuote + 1);

                if (endQuote !== -1) {
                    const value = query.substring(startQuote, endQuote + 1);
                    tokens.push(key + operator + value);
                    i = endQuote + 1;
                    continue;
                }
            }

            // Handle regular tokens (keywords, conditions, etc.)
            let token = "";
            while (
                i < query.length &&
                !/\s/.test(query[i]) &&
                query[i] !== "(" &&
                query[i] !== ")"
            ) {
                token += query[i];
                i++;
            }

            if (token) {
                tokens.push(token);
            }
        }

        return tokens;
    }

    private peek(): string | undefined {
        return this.tokens[this.pos];
    }

    private consume(): string {
        return this.tokens[this.pos++];
    }

    private parseOr(): QueryNode {
        let left = this.parseAnd();

        while (this.peek() === "or") {
            this.consume(); // consume 'or'
            const right = this.parseAnd();
            left = { type: "or", left, right };
        }

        return left;
    }

    private parseAnd(): QueryNode {
        let left = this.parseNot();

        while (this.peek() === "and") {
            this.consume(); // consume 'and'
            const right = this.parseNot();
            left = { type: "and", left, right };
        }

        return left;
    }

    private parseNot(): QueryNode {
        if (this.peek() === "not") {
            this.consume(); // consume 'not'
            const child = this.parseNot();
            return { type: "not", child };
        }

        return this.parsePrimary();
    }

    private parsePrimary(): QueryNode {
        if (this.peek() === "(") {
            this.consume(); // consume '('
            const node = this.parseOr();
            this.consume(); // consume ')'
            return node;
        }

        return this.parseCondition();
    }

    private parseCondition(): QueryNode {
        const token = this.consume();

        // Check for comparison operators
        if (token.includes("<=")) {
            const [key, value] = token.split("<=");
            return { type: "lessOrEqual", key, value: parseFloat(value) };
        } else if (token.includes(">=")) {
            const [key, value] = token.split(">=");
            return { type: "greaterOrEqual", key, value: parseFloat(value) };
        } else if (token.includes("<")) {
            const [key, value] = token.split("<");
            return { type: "less", key, value: parseFloat(value) };
        } else if (token.includes(">")) {
            const [key, value] = token.split(">");
            return { type: "greater", key, value: parseFloat(value) };
        } else if (token.includes("!~")) {
            const [key, rawValue] = token.split("!~");
            const value = removeQuotes(rawValue);
            return { type: "notContains", key, value };
        } else if (token.includes("~")) {
            const [key, rawValue] = token.split("~");
            const value = removeQuotes(rawValue);
            return { type: "contains", key, value };
        } else if (token.includes("!=")) {
            const [key, rawValue] = token.split("!=");
            const value = removeQuotes(rawValue);
            return { type: "notEquals", key, value };
        } else if (token.includes("=")) {
            const [key, rawValue] = token.split("=");
            const value = removeQuotes(rawValue);
            return { type: "equals", key, value };
        }

        throw new Error(`Invalid condition: ${token}`);
    }
}

export function evaluateQuery(track: Track, node: QueryNode): boolean {
    switch (node.type) {
        case "equals": {
            const values = track.tags[node.key];
            if (!values) return false;
            const lowerValue = node.value.toLowerCase();
            return values.some((v) => v.toLowerCase() === lowerValue);
        }

        case "notEquals": {
            const values = track.tags[node.key];
            if (!values) return true;
            const lowerValue = node.value.toLowerCase();
            return !values.some((v) => v.toLowerCase() === lowerValue);
        }

        case "contains": {
            const values = track.tags[node.key];
            if (!values) return false;
            const lowerValue = node.value.toLowerCase();
            return values.some((v) => v.toLowerCase().includes(lowerValue));
        }

        case "notContains": {
            const values = track.tags[node.key];
            if (!values) return true;
            const lowerValue = node.value.toLowerCase();
            return !values.some((v) => v.toLowerCase().includes(lowerValue));
        }

        case "less": {
            const values = track.tags[node.key];
            if (!values || values.length === 0) return false;
            const numValue = parseFloat(values[0]);
            if (isNaN(numValue)) return false;
            return numValue < node.value;
        }

        case "greater": {
            const values = track.tags[node.key];
            if (!values || values.length === 0) return false;
            const numValue = parseFloat(values[0]);
            if (isNaN(numValue)) return false;
            return numValue > node.value;
        }

        case "lessOrEqual": {
            const values = track.tags[node.key];
            if (!values || values.length === 0) return false;
            const numValue = parseFloat(values[0]);
            if (isNaN(numValue)) return false;
            return numValue <= node.value;
        }

        case "greaterOrEqual": {
            const values = track.tags[node.key];
            if (!values || values.length === 0) return false;
            const numValue = parseFloat(values[0]);
            if (isNaN(numValue)) return false;
            return numValue >= node.value;
        }

        case "not": {
            return !evaluateQuery(track, node.child);
        }

        case "and": {
            return (
                evaluateQuery(track, node.left) &&
                evaluateQuery(track, node.right)
            );
        }

        case "or": {
            return (
                evaluateQuery(track, node.left) ||
                evaluateQuery(track, node.right)
            );
        }
    }
}

export function parseQuery(query: string): QueryNode | null {
    const parser = new QueryParser();
    return parser.parse(query);
}

export function query_tracks(tracks: Track[], query: string): Track[] {
    const node = parseQuery(query);

    if (!node) {
        return tracks;
    }

    return tracks.filter((track) => evaluateQuery(track, node));
}
