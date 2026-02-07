export type CEXName = "binance" | "kucoin" | "bybit";
export type ChainId = 1 | 56; // 1 = Ethereum, 56 = BSC

export interface CEXAddressConfig {
  [cexName: string]: {
    [chainId: number]: string[];
  };
}

export const cexAddresses: CEXAddressConfig = {
  binance: {
    1: [
      // Ethereum mainnet - Deduplicated unique addresses
      "0xf977814e90da44bfa03b6295a0616a897441acec",
      "0x18e226459ccf0eec276514a4fd3b226d8961e4d1",
      "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",
      "0x4aec0e98fc1fb55b9cc2faaa7a81acca42cb4e96",
      "0x3a3c006053a9b40286b9951a11be4c5808c11dc8",
      "0x5a52e96bacdabb82fd05763e25335261b270efcb",
      "0x4ed6cf63bd9c009d247ee51224fc1c7041f517f1",
      "0x28c6c06298d514db089934071355e5743bf21d60",
      "0x21a31ee1afc51d94c2efccaa2092ad1028285549",
      "0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d",
      "0xd3a22590f8243f8e83ac230d1842c9af0404c4a1",
      "0x308a2a0712570daeea77c8ba9c27a32cdc4000d4",
      "0x86523c87c8ec98c7539e2c58cd813ee9d1a08d96",
      "0x43684d03d81d3a4c70da68febdd61029d426f042",
      "0x56eddb7aa87536c09ccc2793473599fd21a8b17f",
      "0x4976a4a02f38326660d17bf34b431dc6e2eb2327",
      "0x9696f59e4d72e237be84ffd425dcad154bf96976",
      "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
      "0xa7c0d36c4698981fab42a7d8c783674c6fe2592d",
      "0x4fdfe365436b5273a42f135c6a6244a20404271e",
      "0x835678a611b28684005a5e2233695fb6cbbb0007",
      "0x4a9e49a45a4b2545cb177f79c7381a30e1dc261f",
      "0xa64b436964e7415c0e70b9989a53e1fb9a90e726",
      "0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055",
      "0x38aaef3782910bdd9ea3566c839788af6ff9b200",
      "0x030e37ddd7df1b43db172b23916d523f1599c6cb",
      "0x1b46970cfe6a271e884f636663c257a5a571fb2c",
      "0xad354cfbaa4a8572dd6df021514a3931a8329ef5",
      "0xe1940f578743367f38d3f25c2d2d32d6636929b6",
      "0x87433fec6f8d9df13d1e17c4b11364ecd2e93a51",
      "0xc8daf809c7d7c27dd62d006196d8901ba57e5eae",
    ],
    56: [
      "0x01c952174c24e1210d26961d456a77a39e1f0bb0",
      "0x08439901c2bb071cd0812ed329675c9657434083",
      "0x0e4158c85ff724526233c1aeb4ff6f0c46827fbe",
      "0x161ba15a5f335c9f06bb5bbb0a9ce14076fbb645",
      "0x18e226459ccf0eec276514a4fd3b226d8961e4d1",
      "0x1fbe2acee135d991592f167ac371f3dd893a508b",
      "0x29bdfbf7d27462a2d115748ace2bd71a2646946c",
      "0x3c783c21a0383057d128bae431894a5c19f9cf06",
      "0x43684d03d81d3a4c70da68febdd61029d426f042",
      "0x4aec0e98fc1fb55b9cc2faaa7a81acca42cb4e96",
      "0x4ed6cf63bd9c009d247ee51224fc1c7041f517f1",
      "0x4fdfe365436b5273a42f135c6a6244a20404271e",
      "0x515b72ed8a97f42c568d6a143232775018f133c8",
      "0x5a52e96bacdabb82fd05763e25335261b270efcb",
      "0x631fc1ea2270e98fbd9d92658ece0f5a269aa161",
      "0x73f5ebe90f27b46ea12e5795d16c4b408b19cc6f",
      "0x835678a611b28684005a5e2233695fb6cbbb0007",
      "0x86523c87c8ec98c7539e2c58cd813ee9d1a08d96",
      "0x8894e0a0c962cb723c1976a4421c95949be2d4e3",
      "0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d",
      "0xa180fe01b906a1be37be6c534a3300785b20d947",
      "0xa7c0d36c4698981fab42a7d8c783674c6fe2592d",
      "0xbd612a3f30dca67bf60a39fd0d35e39b7ab80774",
      "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
      "0xbf83d18a46325acb7d8f40a462d23a92f467ed7a",
      "0xd3a22590f8243f8e83ac230d1842c9af0404c4a1",
      "0xdccf3b77da55107280bd850ea519df3705d1a75a",
      "0xe2fc31f816a9b94326492132018c3aecc4a93ae1",
      "0xeb2d2f1b8c558a40207669291fda468e50c8a0bb",
      "0xf977814e90da44bfa03b6295a0616a897441acec"
    ], // BSC - placeholder for future
    137: [
      "0x082489a616ab4d46d1947ee3f912e080815b08da",
      "0x18e226459ccf0eec276514a4fd3b226d8961e4d1",
      "0x290275e3db66394c52272398959845170e4dcb88",
      "0x417850c1cd0fb428eb63649e9dc4c78ede9a34e8",
      "0x43684d03d81d3a4c70da68febdd61029d426f042",
      "0x4ed6cf63bd9c009d247ee51224fc1c7041f517f1",
      "0x4fdfe365436b5273a42f135c6a6244a20404271e",
      "0x505e71695e9bc45943c58adec1650577bca68fd9",
      "0x5a52e96bacdabb82fd05763e25335261b270efcb",
      "0x835678a611b28684005a5e2233695fb6cbbb0007",
      "0x86523c87c8ec98c7539e2c58cd813ee9d1a08d96",
      "0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d",
      "0xa7c0d36c4698981fab42a7d8c783674c6fe2592d",
      "0xb75f972af41d6ff0bcc6b2613b832632de1e418b",
      "0xd3a22590f8243f8e83ac230d1842c9af0404c4a1",
      "0xe7804c37c13166ff0b37f5ae0bb07a3aebb6e245",
      "0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055",
      "0xf708e1eab1a3651b1c73d1bfa2fc54c148328be4",
      "0xf977814e90da44bfa03b6295a0616a897441acec"
    ]
  },
  kucoin: {
    1: [
      // Ethereum mainnet
      "0x061f7937b7b2bc7596539959804f86538b6368dc",
      "0x1692e170361cefd1eb7240ec13d048fd9af6d667",
      "0x41e29c02713929f800419abe5770faa8a5b4dadc",
      "0x446b86a33e2a438f569b15855189e3da28d027ba",
      "0x45300136662dd4e58fc0df61e6290dffd992b785",
      "0x58edf78281334335effa23101bbe3371b6a36a51",
      "0x7491f26a0fcb459111b3a1db2fbfc4035d096933",
      "0x7b915c27a0ed48e2ce726ee40f20b2bf8a88a1b3",
      "0x83c41363cbee0081dab75cb841fa24f3db46627e",
      "0x9f4cf329f4cf376b7aded854d6054859dd102a2a",
      "0xa152f8bb749c55e9943a3a0a3111d18ee2b3f94e",
      "0xaa99fc695eb1bbfb359fbad718c7c6dafc03a839",
      "0xb8e6d31e7b212b2b7250ee9c26c56cebbfbe6b23",
      "0xce0d2213a0eaff4176d90b39879b7b4f870fa428",
      "0xd6216fc19db775df9774a6e33526131da7d19a2c",
      "0xd91efec7e42f80156d1d9f660a69847188950747",
      "0xf16e9b0d03470827a95cdfd0cb8a8a3b46969b91",
      "0xf97deb1c0bb4536ff16617d29e5f4b340fe231df",
      "0x0c32131b67a9306a42e5b66f869bc213d40e43f0",
      "0x2933782b5a8d72f2754103d1489614f29bfa4625",
      "0x189b24f3eb15dc71b4fc57c5914e7e9b3246e449",
      "0x37e4d1cd3fe31edf473ebcf3b6a75f419c8839d1",
      "0xdd276dc5223d0120f9bf1776f38957cc8da23cb0",
      "0xe8c15aad9d4cd3f59c9dfa18828b91a8b2c49596",
      "0x1b14376ee2d46ae5c27a43d902d96d4f3f264b83",
      "0x3b6d76719a4ea8c53a7a26b50175b8de23c8e956",
      "0xaa10db8804d076601999c7cd769e02e44a99d5b2",
      "0xb514c67824443868d3a70352398f524ef6af6207",
      "0x0669bcdc8ede4a973ed9b3480aff984de15d2d65",
      "0x175ce6204bfda2a509c7e9c786b74407f569c9cc",
      "0x2677c4c8757da1857cc7cc4071e0e0dd32ccb975",
      "0x44f1b02d78ed39962600df6440cf8eed3e02a96b",
      "0x5b234aaab0f61d346a3ef8faca474c1c19f80c1f",
      "0x651f1d419c548125d7e5456fb61f3df47c29600d",
      "0x69be413d648ae00f0fbd9856f1355e22b36ee5e0",
      "0x6d6cc65e2060d0a280fcd47b6c22ec5636797fec",
      "0x8dac80ce96f69f9762bc450faa4d7fbd5891ae18",
      "0xbee64116bd2b1b6373273d01664fbc5532dad06d",
    ],
    56: [
      "0x3ad7d43702bc2177cc9ec655b6ee724136891ef4",
      "0x53f78a071d04224b8e254e243fffc6d9f2f3fa23",
      "0xb8e6d31e7b212b2b7250ee9c26c56cebbfbe6b23",
      "0xd6216fc19db775df9774a6e33526131da7d19a2c",
      "0xf8ba3ec49212ca45325a2335a8ab1279770df6c0",
      "0x17a30350771d02409046a683b18fe1c13ccfc4a8",
      "0xcded3bb9d2dc98f6e4e772095b48051acfb84df9",
      "0x635308e731a878741bfec299e67f5fd28c7553d9",
      "0x2d964ee844c35a72c6a9d498d54c8a9910cf6914",
      "0x46d85c2e20c4eaa7f60c5e64f8134091cb1b9679",
      "0x2933782b5a8d72f2754103d1489614f29bfa4625",
      "0x175ce6204bfda2a509c7e9c786b74407f569c9cc",
      "0x2677c4c8757da1857cc7cc4071e0e0dd32ccb975",
      "0x69be413d648ae00f0fbd9856f1355e22b36ee5e0",
      "0x6d6cc65e2060d0a280fcd47b6c22ec5636797fec",
      "0x8dac80ce96f69f9762bc450faa4d7fbd5891ae18"
    ],
    137: [
      "0xb8e6d31e7b212b2b7250ee9c26c56cebbfbe6b23",
      "0x17a30350771d02409046a683b18fe1c13ccfc4a8",
      "0x2933782b5a8d72f2754103d1489614f29bfa4625",
      "0xd6216fc19db775df9774a6e33526131da7d19a2c",
      "0x9ac5637d295fea4f51e086c329d791cc157b1c84",
      "0xe58c8d45477d894bb9a1501bb0d0a32af8419eda"
    ],
  },
  bybit: {
    1: [
      // Ethereum mainnet
      "0x412dd3f282b1fa20d3232d86ae060dec644249f6",
      "0x6bd869be16359f9e26f0608a50497f6ef122ee3e",
      "0x922fa922da1b0b28d0af5aa274d7326eaa108c3d",
      "0x88a1493366d48225fc3cefbdae9ebb23e323ade3",
      "0xa7a93fd0a276fc1c0197a5b5623ed117786eed06",
      "0xbaed383ede0e5d9d72430661f3285daa77e9439f",
      "0xee5b5b923ffce93a870b3104b7ca09c3db80047a",
      "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
      "0x6f4565c9d673dbdd379aba0b13f8088d1af3bb0c",
      "0xc22166664e820cda6bf4cedbdbb4fa1e6a84c440",
      "0xdae4fdcb7fc93738ec6d5b1ea92b7c7f75e4f2f6",
      "0x6b9b774502e6afaafcac84f840ac8a0844a1abe3",
      "0x72187db55473b693ded367983212fe2db3768829",
      "0x80a9b4aab0ad3c73cce1c9223236b722db5d6628",
      "0x63bee4a7e4aa5d76dc6ab9b9d1852aabb9a40936",
      "0x33ae83071432116ae892693b45466949a38ac74c",
      "0x801bfd99636ec8961f7e2d2dd0a296d726f5f1ae",
      "0xb829e684df8e31b402a4d4aedf3bbc18a52e7589",
      "0x371c31f9221459e10565cfe78937cbda5db1791c",
      "0xcab3f132a11e5b723fc20ddab8bb1b858d00a8e8",
      "0x25c7d768a7d53e6ebe5590c621437126c766e1ea",
      "0x79ae8c1b31b1e61c4b9d1040217a051f954d4433",
      "0xc273a2e3fc4c8f8610ebe51123dc32d233913da7",
      "0xa9cf4aa55c675badb68519e3cfa8f4be942e6d11",
      "0x6206ae3781f9f1b6fbcf44c7240b1be14f3169ef",
      "0x869bcee3a0bad2211a65c63ec47dbd3d85a84d68",
      "0x30ba21597f22aafa4b0e86c250c8a6eebaf0da54",
      "0x61b2aa17c1c1114e7583bb31f777ff4bdc7ab717",
      "0x3bd0e57e2917d3d9a93f479b3a23b28c3f31a789",
      "0xb24692d17babefd97ea2b4ca604a481a7cc2c8ea",
      "0xc93e48d89f2d6dbc1672908aa68ce7c24d0413b4",
      "0xd860962a96cd471bbe60a83c33e65011d40eb65f",
      "0x933646d78ede6f1ef5cf4a0a03e3a819c8057922",
      "0x3cef1f90be0f15f1573bda7a3e045cca9cff1d15",
      "0x429b41e5eb73e2266affbc2d7a41553bd8f1ede1",
      "0xd7c4d4b3f076bf9fe391190c42676b4dc269ee02",
      "0x4e5e17e8ef17c9a7ef9798ddf78f3a2c38367d16",
      "0x495eb9345788ee6be50c9c36ed67ffa2beb3699f",
      "0x3db4cb6d753d9e0ba7cc84e576d17dcd01b6b67d",
      "0x4e19698c366f7dcd1cfad4d7f621b4d275bb1a6c",
      "0x7c41c7d883dbbe1edfcefca9d7a7592dd30c8b51",
      "0x01e2fb8f565d5e3cb9e0e8f0b607a96169b94393",
      "0x8a2458f32e5ec9935f20e7c2e06e8d4820f726e5",
      "0xc19bb2709321bd6ad6d8396a885b7c151b8d48c5",
      "0x59800fc68c7039566ed7a04b0f735255093cac1d",
      "0x75df67943d35129dd22da5d14fda4983571f553a",
      "0xa0acdf9fa38b293f0bbdd01ca6bf3e7ed8291dd4",
      "0x35696b0847ed8428a098cba726b6514582aa5fc7",
      "0x86dbaa55f0e65857b58109c3cb725deff4da3851",
      "0x8d6d3479c94bb95e737b72186192ff5e7fedf3a2",
      "0xf2f40c3bb444288f6f64d8336dcc14dbd929fd94",
      "0x70f58622158d7e609ae5839c4ad0d477f468863f",
      "0xbce9aecd3985d4cbb9d273453159a26301fa02ef",
      "0xcbf446565eddf074b2c99e8f1c15582a0bfe6eba",
      "0x036c43bebe5fa5dff3c299584b4a6c1923c7d932",
      "0x18e296053cbdf986196903e889b7dca7a73882f6",
      "0x260b364fe0d3d37e6fd3cda0fa50926a06c54cea",
      "0xa1abfa21f80ecf401bd41365adbb6fef6fefdf09",
      "0x70167b76543c4a12b49b2f2b70cbf04d99345786",
      "0x4865d4bcf4ab92e1c9ba5011560e7d4c36f54106",
      "0xc6c6a48ee8e9f593724161c72414d76e94cda93f",
      "0xefef30bd1cca520619306c95091ab18473febc5c",
      "0x180a1b935d28494f9ff4233985562b18b3dcfa74",
      "0xad85405cbb1476825b78a021fa9e543bf7937549",
      "0x8fa129f87b8a11ee1ca35abd46674f8b66984d4a",
      "0x651641299c7ec0aa44ad7ed9b7e12702fed2022f",
      "0x187c9fbf5bd0f266883c03f320260c407c7b4100",
      "0xa4b9569bf942c3aad23c0c2d322fe4aff8e1bf30",
      "0x6522b7f9d481eceb96557f44753a4b893f837e90",
      "0xa31231e727ca53ff95f0d00a06c645110c4ab647",
      "0xf42aac93ab142090db9fdc0bc86aab73cb36f173",
      "0x93228d328c9c74c2bfe9f97638bbb5ef322f2bd5",
      "0x9cdb59516b37f5c1bd166bc41c5b9f68a57225bd",
      "0x0ac92eb5716516a08e7760d314d42e1d5d3c03ae",
      "0x18673311fec54ac2244a602e6d91845553d24e62",
      "0x7a84c1f1aa344d466b0f161f57b0321b98faf6ee",
      "0xc63fe58d36bef77a9a98df32a547537f45aac71d",
      "0xf8f061cfc030928a4acb8c4980911b4f5afc4002",
      "0x1c3944173abee256456b1498299fc501ad5bbd6f",
      "0x13f52026493dccf09065952d44101c3e42b41dda",
      "0x3ef28b7e18c510b8fa031d7f8a1bb24a83ccceb0",
      "0x25c76fa90e90f5a5a6914da07baed9a9647c3dfd",
      "0xf833685f98eba1b99947d418c9512d27c8193b1a",
      "0xa9acc15d8b74a01e5605eb0f1e815ba98e3a16af",
      "0xdba34cfc849738b2075fd28446902d3f1689c09d",
      "0x448c642074d7be4c5fc25929bb5536f772cd9d5c",
      "0x695f7dea85bf8c0aaafef0a9484e74834e28ce8b",
      "0x495c70e181c45f80806dcbd733140361a0f75cc2",
      "0x36cf90ac2d130b987aff0bded378525be36d9686",
      "0x77439637cac35bedd63fc9e769d7819ca1d24a48",
      "0x855e9a74196764ab41adb3e3b76eaf9e3d6d6d48",
      "0x35bf33df55472938ad314678962b7c69204f0a8a",
      "0x8c28e696c89200d423f9a5eea7347747e78ed25f",
      "0x80d45515a84e762c6497a089913f26b41235bf65",
      "0x5c4e79cc7d5b66effcbb19e22cae0c92bff7276d",
      "0x8859eb340330492cb66f3b193e22696de8251e66",
      "0xe46620553d6b28e5d2520b366942990d8654f243",
      "0xa4287bc8a021025974a642806cf2ab717b857380",
      "0x89688768bf9e2e809ca3ac7e22fe5d2f849ef822",
      "0x8ed5b6bc3d85be31209fac182466e0bcc30ba3eb",
      "0x076d55c8998da29531ef7fcac2a01fa21582eed2",
      "0xf358d867bf928cb06408ff2b7564fce336e24de8",
    ],
    56: [
      "0x88a1493366d48225fc3cefbdae9ebb23e323ade3",
      "0xee5B5B923fFcE93A870B3104b7CA09c3db80047A",
      "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
      "0x388E52979AC487c6BdaFCC84B251976Cd162790b",
      "0xd860962a96Cd471BbE60A83c33e65011D40eB65f",
      "0x933646D78ede6F1EF5CF4a0a03e3a819c8057922",
      "0xc19bb2709321bd6ad6d8396a885b7c151b8d48c5",
      "0xc3121c4ca7402922e025e62e9bb4d5b244303878",
      "0xef3aeff9a5f61c6dda33069c58c1434006e13b20",
      "0x318d2aae4c99c2e74f7b5949fa1c34df837789b8",
      "0xc851a293ed8b8888a2e4140744973dd23bbcbaf2"
    ],
    137: [
      "0x88a1493366d48225fc3cefbdae9ebb23e323ade3",
      "0xee5B5B923fFcE93A870B3104b7CA09c3db80047A",
      "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
      "0xd860962a96Cd471BbE60A83c33e65011D40eB65f",
      "0x933646D78ede6F1EF5CF4a0a03e3a819c8057922",
      "0xa85c29b94f8a22a7268facee89ef4eca051be2ce",
      "0x1347378b1d0eb69d3462e09b3dfa2fe28ebe74ec"
    ]
  },
};

/**
 * 
 * @param cexName name of the centralized exchneg
 * @param chainId id of the network 
 * @returns retrun the set of the that centralized exchange all the address for that network
 */
export function getCEXAddressSet(cexName: CEXName, chainId: number): Set<string> {
  const addresses = cexAddresses[cexName]?.[chainId] ?? [];
  return new Set(addresses.map((addr) => addr.toLowerCase()));
}

/**
 * 
 * @param chainId 
 * @returns 
 */
export function getCEXAddressSetsForChain(
  chainId: number
): Map<CEXName, Set<string>> {
  const result = new Map<CEXName, Set<string>>();
  for (const [cexName, chains] of Object.entries(cexAddresses)) {
    if (chains[chainId] && chains[chainId].length > 0) {
      result.set(
        cexName as CEXName,
        new Set(chains[chainId].map((a) => a.toLowerCase()))
      );
    }
  }
  return result;
}

/**
 * Get all the cex address
 * @param chainId network id numbre 
 * @returns a set of all the cex address
 */
export function getAllCEXAddressesForChain(chainId: number): Set<string> {
  const all = new Set<string>();
  for (const chains of Object.values(cexAddresses)) {
    for (const addr of chains[chainId] ?? []) {
      all.add(addr.toLowerCase());
    }
  }
  return all;
}

