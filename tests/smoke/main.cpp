// Host that exercises what every consumer needs from an engine build: the message callback, a native call
// (or the generic one in portable mode), script classes, recursion and the context.
#include <angelscript.h>

#include <cstdio>
#include <cstring>

static int Twice(int value)
{
    return value * 2;
}

static void TwiceGeneric(asIScriptGeneric* gen)
{
    gen->SetReturnDWord(static_cast<asDWORD>(static_cast<int>(gen->GetArgDWord(0)) * 2));
}

static void PrintGeneric(asIScriptGeneric* gen)
{
    std::printf("%d\n", static_cast<int>(gen->GetArgDWord(0)));
}

static void Message(const asSMessageInfo* info, void*)
{
    std::fprintf(stderr, "%s (%d, %d): %s\n", info->section, info->row, info->col, info->message);
}

static const char* const kScript = R"(
class Counter
{
    int n;
    Counter() { n = 0; }
    void add(int v) { n += v; }
    int get() const { return n; }
}

int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }

int main()
{
    Counter c;
    for (int i = 1; i <= 10; i++)
        c.add(i);
    print(c.get());
    return fib(10) + c.get() + twice(3);
}
)";

int main()
{
    asIScriptEngine* engine = asCreateScriptEngine();
    if (!engine)
        return 2;
    engine->SetMessageCallback(asFUNCTION(Message), nullptr, asCALL_CDECL);

    const bool portable = std::strstr(asGetLibraryOptions(), "AS_MAX_PORTABILITY") != nullptr;
    int r = engine->RegisterGlobalFunction("void print(int)", asFUNCTION(PrintGeneric), asCALL_GENERIC);
    r = r < 0 ? r : (portable ? engine->RegisterGlobalFunction("int twice(int)", asFUNCTION(TwiceGeneric), asCALL_GENERIC)
                              : engine->RegisterGlobalFunction("int twice(int)", asFUNCTION(Twice), asCALL_CDECL));
    if (r < 0)
        return 3;

    asIScriptModule* module = engine->GetModule("smoke", asGM_ALWAYS_CREATE);
    if (module->AddScriptSection("smoke", kScript) < 0 || module->Build() < 0)
        return 4;
    asIScriptFunction* entry = module->GetFunctionByDecl("int main()");
    if (!entry)
        return 5;
    asIScriptContext* context = engine->CreateContext();
    if (context->Prepare(entry) < 0 || context->Execute() != asEXECUTION_FINISHED)
        return 6;
    const int result = static_cast<int>(context->GetReturnDWord());
    context->Release();
    engine->ShutDownAndRelease();
    std::printf("engine %s, %s calls, result %d\n", asGetLibraryVersion(), portable ? "generic" : "native", result);
    return result == 116 ? 0 : 7;
}
