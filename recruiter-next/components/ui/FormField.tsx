"use client";

import { createContext, useContext, useId, type ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

interface FormFieldContextValue {
  /** id to put on the control, so the <label> can point at it */
  controlId?: string;
  /** id of the error/hint text, for aria-describedby */
  descriptionId?: string;
  hasError?: boolean;
}

const FormFieldContext = createContext<FormFieldContextValue>({});

/**
 * Consumed by form controls (see Input) so they can wire themselves to the
 * surrounding label and error text without the caller passing ids by hand.
 */
export function useFormField() {
  return useContext(FormFieldContext);
}

export interface FormFieldProps {
  label?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
}

/**
 * Label + control + error/hint wrapper.
 *
 * The Svelte original rendered a bare `<label>` next to its slot with no
 * association between them, suppressed via
 * `svelte-ignore a11y_label_has_associated_control` — so clicking the label did
 * nothing and screen readers announced the control unlabelled
 * (MIGRATION.md debt #8). Here `useId()` generates the ids and passes them down
 * through context, so the markup is correct without changing call sites.
 */
export function FormField({
  label,
  error,
  hint,
  required = false,
  children,
  className,
}: FormFieldProps) {
  const controlId = useId();
  const descriptionId = useId();
  const description = error ?? hint;

  return (
    <FormFieldContext.Provider
      value={{
        controlId,
        descriptionId: description ? descriptionId : undefined,
        hasError: Boolean(error),
      }}
    >
      <div className={cn("space-y-1.5", className)}>
        {label && (
          <label
            htmlFor={controlId}
            className="block text-sm font-medium text-black"
          >
            {label}
            {required && <span className="text-error">*</span>}
          </label>
        )}

        {children}

        {error ? (
          <p id={descriptionId} className="text-sm text-error">
            {error}
          </p>
        ) : hint ? (
          <p id={descriptionId} className="text-sm text-muted">
            {hint}
          </p>
        ) : null}
      </div>
    </FormFieldContext.Provider>
  );
}

export default FormField;
