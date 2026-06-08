import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { TextArea } from ".";

const meta: Meta<typeof TextArea> = {
  title: "Molecules/TextArea",
  component: TextArea,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  decorators: [(Story) => <div style={{ width: "360px" }}><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof TextArea>;

export const Default: Story = {
  render: () => {
    const [v, setV] = useState("");
    return <TextArea id="desc" label="Beschreibung" value={v} onChange={setV} placeholder="Was passiert in dieser Szene…" />;
  },
};

export const WithCharCount: Story = {
  render: () => {
    const [v, setV] = useState("Ein kurzer Text.");
    return (
      <TextArea
        id="summary"
        label="Zusammenfassung"
        value={v}
        onChange={setV}
        maxLength={200}
        showCharCount
        helperText="Kurze Zusammenfassung für den Überblick."
      />
    );
  },
};

export const AutoResize: Story = {
  render: () => {
    const [v, setV] = useState("Dieser Text wächst mit…");
    return (
      <TextArea
        id="notes"
        label="Notizen"
        value={v}
        onChange={setV}
        autoResize
        rows={2}
        placeholder="Tippe hier…"
      />
    );
  },
};

export const WithError: Story = {
  render: () => (
    <TextArea
      id="x"
      label="Inhalt"
      value=""
      onChange={() => {}}
      errorMessage="Dieses Feld darf nicht leer sein."
    />
  ),
};

export const Disabled: Story = {
  render: () => (
    <TextArea
      id="x"
      label="Gesperrt"
      value="Inhalt kann nicht geändert werden."
      onChange={() => {}}
      disabled
    />
  ),
};
