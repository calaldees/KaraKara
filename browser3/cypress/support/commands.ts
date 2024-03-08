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
    (room?: string, password?: string, booth?: boolean) => {
        cy.visit("/");
        cy.get("h1").dblclick();
        cy.get("[data-cy=room-input]").type(room || "test");
        cy.get("[data-cy=password-input]").type(password || room || "test");
        booth && cy.get("[data-cy=booth-input]").check();
        cy.get("[data-cy=save-button]").click();
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
            login(room?: string, password?: string, booth?: boolean): Chainable;
            //       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
            //       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
            //       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
        }
    }
}
