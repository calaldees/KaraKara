/// <reference types="cypress" />

export {};

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
Cypress.Commands.add(
    "login",
    (room: string, username: string, password: string) => {
        cy.session(
            [room, username, password],
            () => {
                cy.visit("/");
                cy.contains("demo").should("not.exist");

                cy.get('[data-cy="user-icon"]').click();
                cy.get('[placeholder="User Name"]').type(username);
                cy.get('[placeholder="Password"]').type(password);
                cy.get('[value="Log In"]').click();
                cy.contains(username).should("exist");
            },
            {
                validate: () => {
                    cy.visit("/");
                    cy.contains(username).should("exist");
                },
            },
        );
    },
);
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//

declare global {
    namespace Cypress {
        interface Chainable {
            login(room: string, username: string, password: string): Chainable;
            //       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
            //       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
            //       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
        }
    }
}
